"""End-to-end test of the GitHub updater (updater/iw-update.ps1).

A local HTTP server stands in for GitHub: it serves this working tree as the
latest commit through the same API, raw-file and archive URLs the updater
uses. The test then updates real installations and checks the result:

  1. A source install of 0.5.4 (commit d3ad40c) is updated: every file must
     end up identical to the working tree, files 0.5.4 had that the game no
     longer ships must be gone, and the server's own admins.txt is untouched.
  2. A second update downloads only what was changed by hand, and treats a
     file converted to CRLF line endings as unchanged.
  3. A third update finds nothing to do.
  4. An update whose download fails changes nothing and reports the failure.
  5. A release-folder install gets only the files a release holds, with the
     client's content under content/ rather than iwserver/content/.

It needs PowerShell (pwsh, or the path in IW_PWSH); without it, it only runs
the static checks. The game itself runs the script with Windows PowerShell
5.1, so the script avoids anything newer than 5.1.
"""
import hashlib
import http.server
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "updater" / "iw-update.ps1"
REPO = "shywolfee/infinite-warfare"
OLD_COMMIT = "d3ad40c"
STATE = {"updater/last_update.txt", "updater/last_update.log", "updater/installed_files.txt"}
PROTECTED = {"iwserver/admins.txt", "iwserver/motd.svr", "iwserver/currentmap.txt"}
problems: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        problems.append(message)


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


# Static checks that need nothing installed.
client = (ROOT / "Infinite Warfare.nvgt").read_text(encoding="utf-8", errors="replace")
updater = (ROOT / "includes" / "updater.nvgt").read_text(encoding="utf-8")
release = (ROOT / "includes" / "release_tools.nvgt").read_text(encoding="utf-8")
script_text = SCRIPT.read_text(encoding="utf-8")
version = (ROOT / "version.txt").read_text(encoding="utf-8").strip()
check(f'string version_name="{version}";' in client, "version.txt does not match the client's version_name")
check("string local_version=version_name;" in updater, "the updater judges the installed version by a file, not the running program")
for parameter in ("-Root", "-Restart", "-Mode", "-Repository", "-Branch"):
    check(f'"{parameter}"' in updater and f"${parameter[1:]}" in script_text, f"the client and script disagree about {parameter}")
check("updater_remove_retired_files();" in client and client.index("updater_remove_retired_files();") < client.index("load_all_weapons();"),
      "retired files must be removed before content loads")
check("updater_report_last_result();" in client, "the client never reports the last update's result")
check('"iw-update.ps1","retired_files.txt"' in release, "release builds do not ship the updater")
script_code = "\n".join(line for line in script_text.splitlines() if not line.lstrip().startswith("#"))
for name in ("??", "-AsHashtable", "ForEach-Object -Parallel", "&&", "||"):
    check(name not in script_code.replace('"', ""), f"iw-update.ps1 uses {name}, which Windows PowerShell 5.1 lacks")
# 5.1 throws if User-Agent or Accept is passed in -Headers.
check("-Headers" not in script_code, "iw-update.ps1 passes -Headers; Windows PowerShell 5.1 refuses User-Agent there, use -UserAgent")
if git("rev-parse", "--is-shallow-repository").strip() == b"false":
    result = subprocess.run(["python3", str(ROOT / "tools" / "update_retired_files.py"), "--check"], capture_output=True, text=True)
    check(result.returncode == 0, result.stdout + result.stderr)

pwsh = os.environ.get("IW_PWSH") or shutil.which("pwsh")


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# The "remote": this working tree, tracked files plus new ones not yet committed.
names = [n for n in git("ls-files", "-z", "--cached", "--others", "--exclude-standard").decode().split("\0") if n]
REMOTE = {n: (ROOT / n).read_bytes() for n in names if (ROOT / n).is_file()}
SHA = "f" * 40
failing: set[str] = set()


class FakeGitHub(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, body: bytes, code: int = 200, kind: str = "application/octet-stream"):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        from urllib.parse import unquote, urlsplit
        path = unquote(urlsplit(self.path).path)
        if path == f"/api/repos/{REPO}/commits/main":
            return self.send(json.dumps({"sha": SHA}).encode(), kind="application/json")
        if path == f"/api/repos/{REPO}/git/trees/{SHA}":
            tree = [{"path": n, "type": "blob", "mode": "100644", "sha": blob_sha(d)} for n, d in REMOTE.items()]
            return self.send(json.dumps({"sha": SHA, "tree": tree, "truncated": False}).encode(), kind="application/json")
        prefix = f"/raw/{REPO}/{SHA}/"
        if path.startswith(prefix):
            name = path[len(prefix):]
            if name in failing or name not in REMOTE:
                return self.send(b"not found", 404)
            return self.send(REMOTE[name])
        if path == f"/archive/{REPO}/archive/{SHA}.zip":
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
                for n, d in REMOTE.items():
                    z.writestr(f"infinite-warfare-{SHA}/{n}", d)
            return self.send(buffer.getvalue())
        self.send(b"not found", 404)


def run_update(install: Path, threshold: int = 150) -> dict:
    subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), "-Root", str(install),
                    "-Mode", "source", "-ApiBase", f"{BASE}/api", "-RawBase", f"{BASE}/raw",
                    "-ArchiveBase", f"{BASE}/archive", "-ArchiveThreshold", str(threshold), "-WaitSeconds", "2"],
                   capture_output=True, text=True, timeout=900)
    text = (install / "updater" / "last_update.txt").read_text(encoding="utf-8")
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


def files_of(folder: Path) -> dict[str, bytes]:
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()}


if pwsh:
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeGitHub)
    BASE = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with tempfile.TemporaryDirectory() as temp:
        install = Path(temp) / "Infinite Warfare"
        install.mkdir()
        archive = git("archive", "--format=zip", OLD_COMMIT)
        zipfile.ZipFile(io.BytesIO(archive)).extractall(install)
        old_files = set(files_of(install))
        (install / "iwserver" / "admins.txt").write_text("my own admins\n", encoding="utf-8")
        shutil.copytree(ROOT / "updater", install / "updater", dirs_exist_ok=True)

        # 1. 0.5.4 to now.
        result = run_update(install)
        check(result.get("status") == "updated", f"update from 0.5.4 failed: {result}")
        have = files_of(install)
        for name, data in REMOTE.items():
            if name in PROTECTED:
                continue
            check(have.get(name) == data, f"after updating from 0.5.4, {name} does not match")
        retired = (ROOT / "updater" / "retired_files.txt").read_text(encoding="utf-8").split()
        leftovers = sorted(n for n in have if n not in REMOTE and n not in STATE and n in old_files)
        check(not leftovers, f"files 0.5.4 shipped and the game no longer does were left behind: {leftovers[:5]}")
        check(any(r in old_files for r in retired), "the 0.5.4 install had no retired files to remove; the test proves nothing")
        check((install / "iwserver" / "admins.txt").read_text(encoding="utf-8") == "my own admins\n", "the update overwrote iwserver/admins.txt")

        # 2. Only what changed is downloaded; CRLF is not a change.
        text_file = install / "changes.txt"
        text_file.write_bytes(text_file.read_bytes().replace(b"\n", b"\r\n"))
        (install / "README.md").write_text("edited by hand\n", encoding="utf-8")
        (install / "rules.txt").unlink()
        result = run_update(install, threshold=1000)
        check(result.get("status") == "updated" and result.get("changed") == "2",
              f"a two-file change downloaded {result.get('changed')} files: {result}")
        check((install / "README.md").read_bytes() == REMOTE["README.md"] and (install / "rules.txt").exists(), "per-file update did not restore the files")

        # 3. Nothing to do.
        result = run_update(install)
        check(result.get("status") == "current", f"an up-to-date install was not reported current: {result}")

        # 4. A failed download changes nothing.
        (install / "README.md").write_text("edited again\n", encoding="utf-8")
        (install / "developers.txt").write_text("edited too\n", encoding="utf-8")
        failing.add("developers.txt")
        result = run_update(install, threshold=1000)
        failing.clear()
        check(result.get("status") == "failed", f"a failed download was not reported: {result}")
        check((install / "README.md").read_text(encoding="utf-8") == "edited again\n", "a failed update still changed files")

        # 5. A release folder.
        release_dir = Path(temp) / "release"
        (release_dir / "content" / "weapons").mkdir(parents=True)
        (release_dir / "Infinite Warfare.exe").write_bytes(b"old program")
        stale = "content/" + next(r for r in retired if r.startswith("iwserver/content/weapons/"))[len("iwserver/content/"):]
        (release_dir / stale).parent.mkdir(parents=True, exist_ok=True)
        (release_dir / stale).write_text("stale", encoding="utf-8")
        shutil.copytree(ROOT / "updater", release_dir / "updater", dirs_exist_ok=True)
        result = run_update(release_dir)
        have = files_of(release_dir)
        check(result.get("status") == "updated", f"release update failed: {result}")
        check(not (release_dir / "iwserver").exists(), "a release folder was given the server and source tree")
        check(have.get("Infinite Warfare.exe") == REMOTE["Infinite Warfare.exe"], "the release executable was not updated")
        weapons = [n for n in REMOTE if n.startswith("iwserver/content/weapons/")]
        check(all(have.get("content/weapons/" + n[len("iwserver/content/weapons/"):]) == REMOTE[n] for n in weapons),
              "release weapon files are not under content/weapons")
        check(stale not in have, "a retired weapon file survived in a release folder")
    server.shutdown()

assert not problems, "\n".join(problems)
print("PASS updater: static checks" + (" and five end-to-end updates" if pwsh else " (no PowerShell; end-to-end updates skipped)"))
