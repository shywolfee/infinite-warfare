"""Runs the repository status screen's data layer against recorded GitHub replies.

A local HTTP server serves tools/tests/fixtures/github (trimmed real replies
from the GitHub API for this repository, plus one made-up issue) under the
same paths the game asks GitHub for. repo_status_regression.nvgt opens every
view and prints it; this script checks what was printed:

- every section reads its data, with the right counts, links and drill-downs;
- "Your copy" finds the commit of a git checkout through packed-refs and
  lists the commits it is missing;
- "What's new on GitHub" marks the releases newer than the running build,
  including a hotfix heading;
- times parse correctly, Markdown is flattened, replies are cached;
- GitHub's rate-limit reply becomes an explanation, not a blank screen.

It needs NVGT (set NVGT to the executable); without it, it reports a skip.
The Linux build from https://nvgt.dev/downloads runs it.
"""
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tools" / "tests" / "fixtures" / "github"
SLUG = "shywolfee/infinite-warfare"
LOCAL_SHA = "0b131660ec04049c2215677f23717f632c808c9b"
CHANGES = """New in 0.5.9, build 100 (2026-10-06)
Added Repository status to the main menu.

New in 0.5.8, build 99 (2026-10-06)
Rebuilt the GitHub updater.

Hotfix for 0.5.7, build 98 (2026-10-06)
Fixed the client not compiling.

New in 0.5.7, build 97 (2026-10-06)
Vehicles drive like vehicles.
Arenas have been rebuilt.
"""

nvgt = os.environ.get("NVGT") or shutil.which("nvgt")
if not nvgt:
    print("SKIP repository status: set NVGT to an NVGT executable to run it")
    sys.exit(0)

requests: list[str] = []


def fixture(name: str) -> bytes:
    return (FIXTURES / f"{name}.json").read_bytes()


ROUTES = [
    (r"/api/rate_limit", "rate_limit"),
    (rf"/api/repos/{SLUG}", "repo"),
    (rf"/api/repos/{SLUG}/commits/[0-9a-f]+", "commit"),
    (rf"/api/repos/{SLUG}/commits", "commits"),
    (rf"/api/repos/{SLUG}/compare/.+", "compare"),
    (rf"/api/repos/{SLUG}/branches", "branches"),
    (rf"/api/repos/{SLUG}/pulls/1", "pull"),
    (rf"/api/repos/{SLUG}/pulls", "pulls"),
    (rf"/api/repos/{SLUG}/issues/2/comments", "comments"),
    (rf"/api/repos/{SLUG}/issues/2", "issue"),
    (rf"/api/repos/{SLUG}/issues", "issues"),
    (rf"/api/repos/{SLUG}/(releases|tags)", None),
    (rf"/api/repos/{SLUG}/contributors", "contributors"),
    (rf"/api/repos/{SLUG}/languages", "languages"),
    (rf"/api/repos/{SLUG}/events", "events"),
    (rf"/api/repos/{SLUG}/actions/runs", "runs"),
]


# What the game sent: (method, path, Authorization header, body).
sent: list[tuple[str, str, str, str]] = []
state = {"starred": False, "polls": 0}
USER = {"login": "test-player", "name": "Test Player", "html_url": "https://github.com/test-player",
        "public_repos": 4, "followers": 2, "following": 1}
SIGNED_IN_REPO = None


def signed_in_repo() -> bytes:
    repo = json.loads(fixture("repo"))
    repo["permissions"] = {"admin": False, "push": True, "pull": True}
    repo["owner"] = {"login": "shywolfee"}
    return json.dumps(repo).encode()


class FakeGitHub(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, body: bytes, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-RateLimit-Limit", "5000" if self.authorized() else "60")
        self.send_header("X-RateLimit-Remaining", "4990" if self.authorized() else "57")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        return self.headers.get("Authorization") == "Bearer good-token"

    def record(self, method: str) -> tuple[str, str]:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8") if length else ""
        path = urlsplit(self.path).path
        sent.append((method, path, self.headers.get("Authorization") or "", body))
        requests.append(path)
        return path, body

    def do_GET(self):
        path, _ = self.record("GET")
        if path.startswith("/limited/"):
            return self.send(fixture("rate_limited"), 403)
        if path == f"/raw/{SLUG}/main/version.txt":
            return self.send(b"0.5.9\n")
        if path == f"/raw/{SLUG}/main/changes.txt":
            return self.send(CHANGES.encode())
        if path == "/api/user":
            return self.send(json.dumps(USER).encode()) if self.authorized() else self.send(b'{"message":"Bad credentials","documentation_url":"x"}', 401)
        if self.authorized():
            if path == f"/api/repos/{SLUG}":
                return self.send(signed_in_repo())
            if path == f"/api/user/starred/{SLUG}":
                return self.send(b"", 204) if state["starred"] else self.send(b'{"message":"Not Found"}', 404)
            if path == f"/api/repos/{SLUG}/subscription":
                return self.send(b'{"message":"Not Found"}', 404)
            if path == f"/api/repos/{SLUG}/notifications":
                return self.send(json.dumps([
                    {"unread": True, "reason": "subscribed", "updated_at": "2026-10-05T19:30:00Z",
                     "subject": {"title": "Grenades thrown from a moving car land behind it", "type": "Issue",
                                 "url": f"https://api.github.com/repos/{SLUG}/issues/2"}},
                    {"unread": False, "reason": "review_requested", "updated_at": "2026-07-11T17:45:06Z",
                     "subject": {"title": "Builds 0.5.0.1 through 0.5.0.4.1", "type": "PullRequest",
                                 "url": f"https://api.github.com/repos/{SLUG}/pulls/1"}}]).encode())
            if path == "/api/user/repos":
                return self.send(json.dumps([{"full_name": "test-player/infinite-warfare", "private": False, "fork": True,
                                              "stargazers_count": 0, "pushed_at": "2026-10-01T00:00:00Z",
                                              "html_url": "https://github.com/test-player/infinite-warfare"}]).encode())
        for pattern, name in ROUTES:
            if re.fullmatch(pattern, path):
                return self.send(b"[]" if name is None else fixture(name))
        self.send(b'{"message":"Not Found","documentation_url":"https://docs.github.com"}', 404)

    def change(self, method: str):
        path, body = self.record(method)
        if path == "/login-site/login/device/code":
            return self.send(b'{"device_code":"dev-123","user_code":"ABCD-1234","verification_uri":"https://github.com/login/device","expires_in":900,"interval":1}')
        if path == "/login-site/login/oauth/access_token":
            state["polls"] += 1
            return self.send(b'{"error":"authorization_pending"}' if state["polls"] == 1 else b'{"access_token":"good-token","token_type":"bearer","scope":"public_repo,notifications"}')
        if not self.authorized():
            return self.send(b'{"message":"Requires authentication","documentation_url":"x"}', 401)
        if path == f"/api/user/starred/{SLUG}":
            state["starred"] = method == "PUT"
            return self.send(b"", 204)
        if path == f"/api/repos/{SLUG}/issues" and method == "POST":
            json.loads(body)
            return self.send(b'{"number":3}', 201)
        if path == f"/api/repos/{SLUG}/forks":
            return self.send(b'{"message":"Validation Failed","errors":[{"message":"You cannot fork a repository you own"}]}', 422)
        if path == f"/api/repos/{SLUG}/pulls/1/merge":
            return self.send(b'{"sha":"abcdef1234567890","merged":true,"message":"Pull Request successfully merged"}')
        return self.send(b"{}", 201 if method == "POST" else 200)

    def do_POST(self):
        self.change("POST")

    def do_PUT(self):
        self.change("PUT")

    def do_PATCH(self):
        self.change("PATCH")

    def do_DELETE(self):
        self.change("DELETE")


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeGitHub)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_address[1]}"

with tempfile.TemporaryDirectory(prefix="iw-repo-status-") as temp:
    work = Path(temp)
    # The data layer and what it needs, without the curl plugin pragma: the
    # Linux NVGT has url_get built in and no plugin to load.
    (work / "includes").mkdir()
    (work / "tools" / "tests").mkdir(parents=True)
    for name in ("changelog.nvgt", "updater.nvgt", "repo_status.nvgt"):
        text = (ROOT / "includes" / name).read_text(encoding="utf-8")
        (work / "includes" / name).write_text(text.replace("#pragma plugin nvgt_curl", ""), encoding="utf-8")
    shutil.copy2(ROOT / "tools" / "tests" / "repo_status_regression.nvgt", work / "tools" / "tests")
    install = work / "install"
    (install / ".git").mkdir(parents=True)
    (install / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (install / ".git" / "packed-refs").write_text(f"# pack-refs with: peeled fully-peeled sorted\n{LOCAL_SHA} refs/heads/main\n", encoding="utf-8")
    # NVGT runs a script from its own folder, so its settings go beside it.
    data = work / "data"
    data.mkdir()
    (work / "tools" / "tests" / "repo_status_regression.txt").write_text(f"{base}\n{install}\n{data}\n", encoding="utf-8")
    runner = work / "tools" / "tests" / "repo_status_regression.nvgt"
    result = subprocess.run([nvgt, str(runner)], cwd=work, capture_output=True, text=True, timeout=300)
    if "Compilation error" in result.stdout + result.stderr:
        # An NVGT older than the game's (the Linux dev build) lacks some APIs;
        # the compile check's stubs stand in for them.
        shutil.copy2(ROOT / "tools" / "compile_check" / "nvgt_dev_stubs.nvgt", runner.parent)
        runner.write_text('#include "nvgt_dev_stubs.nvgt"\n' + runner.read_text(encoding="utf-8"), encoding="utf-8")
        result = subprocess.run([nvgt, str(runner)], cwd=work, capture_output=True, text=True, timeout=300)
server.shutdown()

output = result.stdout
if os.environ.get("IW_SHOW"):
    print(output)
problems: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        problems.append(message)


if result.returncode != 0 or "VIEW " not in output:
    print(output[-3000:], result.stderr[-3000:])
    raise SystemExit("repo_status_regression.nvgt did not run")

views: dict[str, dict] = {}
current = None
for line in output.splitlines():
    if line.startswith("VIEW "):
        current = {"lines": [], "opens": [], "urls": []}
        views.setdefault(line[5:], []).append(current)
    elif current is not None and line.startswith(("TITLE ", "URL ", "MORE ")):
        key, _, value = line.partition(" ")
        current[key.lower()] = value
    elif current is not None and line.startswith("LINE "):
        text, url, opens = (line[5:].split(" | ") + ["", ""])[:3]
        current["lines"].append(text)
        current["urls"].append(url)
        current["opens"].append(opens)


def view(name: str, index: int = 0) -> dict:
    return views.get(name, [{"lines": [], "opens": [], "urls": []}])[index]


def has(name: str, fragment: str, index: int = 0) -> bool:
    return any(fragment in l for l in view(name, index)["lines"])


def value(prefix: str) -> str:
    return next((l[len(prefix):] for l in output.splitlines() if l.startswith(prefix)), "")


check(value("TIME ") == "1791250445 946684799 -1", f"times parse wrongly: {value('TIME ')}")
check(value("CIVIL ") == "2024-2-29", f"dates convert wrongly: {value('CIVIL ')}")
check(value("TEXT ") == "Subject line | A body wrapped at 72 columns. | - an item that wraps | Heading | See the docs and a picture. Generated by Claude Code | Co-Authored-By: A <a@b> | Claude-Session: https://s",
      f"free text is not joined into paragraphs: {value('TEXT ')}")
check(value("PLAIN ") == "Bold code heading / - item / []", f"Markdown is not flattened: {value('PLAIN ')}")
check("3 stars, 2 forks" in value("HEADLINE ") and "Version 0.5.9 is out; you have 0.5.8" in value("HEADLINE "),
      f"headline: {value('HEADLINE ')}")

check(has("overview", "Repository: shywolfee/infinite-warfare, public") and has("overview", "Licence: none stated")
      and has("overview", "Default branch: main"), "the overview is incomplete")
check(not has("overview", "Description:"), "an empty description is shown")

check(has("copy", "GitHub has version 0.5.9") and has("copy", "commit 0b13166, a git checkout of main"),
      f"your copy did not find the checkout's commit: {view('copy')['lines']}")
check(has("copy", "The main branch has 2 commits you do not have"), "your copy does not count the missing commits")
check(sum(1 for o in view("copy")["opens"] if o.startswith("commit:")) == 3, "the missing commits cannot be opened")

wn = view("whatsnew")
check(wn["lines"][:1] == ["1 release on GitHub is newer than yours. Check for updates installs them."], f"what's new: {wn['lines'][:2]}")
check(wn["lines"][1].startswith("New to you: 0.5.9, 1 change"), "the newer release is not marked")
check(any(l.startswith("0.5.7 hotfix, 1 change") for l in wn["lines"]), "the hotfix heading is not its own release")
check(view("changelog:0")["lines"] == ["Added Repository status to the main menu."], "a release's changes cannot be read")

commits = view("commits:main:1")
check(len(commits["lines"]) == 3 and all(o.startswith("commit:") for o in commits["opens"]), "recent commits are wrong")
check(", by claude, " in commits["lines"][0] and commits["lines"][0].endswith(", bdc9f33"), f"commit line: {commits['lines'][0]}")
check(commits["more"] == "", "three commits should not offer another page")
c = view("commit:bdc9f33")
check(has("commit:bdc9f33", "3 files changed: 14 lines added, 4 lines removed.") and has("commit:bdc9f33", "Infinite Warfare.nvgt, modified"),
      f"commit detail: {c['lines'][:4]}")

check(has("branches", "main, the main branch") and has("branches", "claude/blissful-albattani-3txqg2, identical to main"), "branches")
check(has("branch:claude/blissful-albattani-3txqg2", "has 2 commits that main does not"), "branch comparison")

check(has("pulls", "#1 Builds 0.5.0.1 through 0.5.0.4.1") and has("pulls", "merged"), "pull requests")
check(has("pull:1", "Description:") and has("pull:1", "- 0.5.0.1: Fix jumping") and has("pull:1", "No comments."), f"pull detail: {view('pull:1')['lines'][:6]}")

issues = view("issues")
check(len(issues["lines"]) == 1 and issues["lines"][0].startswith("#2 Grenades thrown from a moving car"), f"issues should skip pull requests: {issues['lines']}")
check(has("issue:2", "Labels: bug, vehicles") and has("issue:2", "1 comment:") and has("issue:2", "shywolfee commented"), "issue detail")
check(has("issue:2", "  I threw a frag grenade out of the jeep window") and not has("issue:2", "**"), "issue text keeps Markdown")

check(has("releases", "no GitHub releases or tags"), "releases without any")
check(has("contributors", "claude, 117 commits") and has("contributors", "shywolfee, 59 commits"), "contributors")
check(has("checks", "runs no automated checks"), "checks without runs")
check(view("languages")["lines"][1].startswith("Python: 71.6 percent"), f"languages are not largest first: {view('languages')['lines']}")
check(has("activity", "shywolfee pushed to claude/blissful-albattani-3txqg2") and has("activity", "merged pull request #1")
      and has("activity", "example-player starred the repository"), f"activity: {view('activity')['lines']}")
check(has("allowance", "57 of 60 requests are left this hour"), "request allowance")

check(value("REQUESTS ") == value("CACHED "), "opening the overview again asked GitHub again instead of using the cache")
check(has("pulls", "GitHub allows 60 requests an hour", 1), f"a rate-limited reply is not explained: {view('pulls', 1)['lines']}")

# Signing in.
check(value("AUTHORIZE ") == "true false false false", f"the token could go somewhere other than GitHub's API: {value('AUTHORIZE ')}")
check(has("account", "You are not signed in") and "ACTION signin" in output, "the signed-out account view does not offer sign-in")
check(value("SIGNEDOUT ") == "Sign in to GitHub first, from Your GitHub account.", f"a change while signed out: {value('SIGNEDOUT ')}")
check("not set up for this copy" in value("NODEVICE "), "browser sign-in without a client ID should explain itself")
check("did not accept that token" in value("BADTOKEN "), f"a bad token: {value('BADTOKEN ')}")
check(value("GOODTOKEN ") == "[] test-player", f"a good token with spaces around it: {value('GOODTOKEN ')}")
check(value("STORED ") == "true", "the token is stored readable, or not at all")
check(value("LOADED ") == "good-token test-player", "the stored sign-in does not load back")
check("Signed in as test-player." in value("HEADLINE2 "), "the headline does not say who is signed in")
check(has("account", "Signed in as test-player, Test Player.", 1) and has("account", "4990 of 5000 GitHub requests are left", 1), f"account: {view('account', 1)['lines']}")
check(has("overview", "You have not starred the repository, and are not watching it.", -1) and has("overview", "You can push to this repository", -1), "signed-in overview")
ov = output[output.index("VIEW overview", output.index("GOODTOKEN")):]
ov = ov[:ov.index("END")]
for action in ("ACTION star |", "ACTION watch |", "ACTION fork |", "ACTION newissue |"):
    check(action in ov, f"the overview lacks {action}")
iss = output[output.index("VIEW issue:2", output.index("GOODTOKEN")):]
check("ACTION comment:2 |" in iss[:iss.index("END")] and "ACTION close:issue:2 |" in iss[:iss.index("END")], "issue actions")
pr = output[output.index("VIEW pull:1", output.index("GOODTOKEN")):]
check("ACTION reopen:pull:1" not in pr[:pr.index("END")], "a merged pull request offered reopening")
check(has("notifications", "Unread: Grenades thrown from a moving car land behind it, subscribed") and "issue:2" in view("notifications")["opens"]
      and "pull:1" in view("notifications")["opens"] and "ACTION readall" in output, f"notifications: {view('notifications')['lines']}")
check(has("myrepos", "test-player/infinite-warfare, a fork, 0 stars"), "your repositories")
expect = {"star": "Starred.", "watch": "You are watching the repository.", "newissue": "Opened issue #3.",
          "notitle": "An issue needs a title.", "comment": "Comment posted.", "close": "Closed.", "reopen": "Reopened.",
          "merge": "Merged as commit abcdef1.", "readall": "Marked as read.", "fork": "GitHub could not do that: Validation Failed: You cannot fork a repository you own",
          "signout": "Signed out."}
for key, text in expect.items():
    check(value(f"DO {key}: ").startswith(text), f"{key}: {value(f'DO {key}: ')}")
bodies = {(m, p): body for m, p, a, body in sent}
issue_body = bodies.get(("POST", f"/api/repos/{SLUG}/issues"), "")
check(json.loads(issue_body or "{}") == {"title": 'Quotes "here" and a back\\slash', "body": "Line one\nLine two\twith a tab"}, f"the new issue was sent as {issue_body!r}")
check(json.loads(bodies.get(("PATCH", f"/api/repos/{SLUG}/issues/2"), "{}")) == {"state": "closed"}, "closing")
check(json.loads(bodies.get(("PATCH", f"/api/repos/{SLUG}/pulls/1"), "{}")) == {"state": "open"}, "reopening a pull request")
check(("PUT", f"/api/user/starred/{SLUG}") in bodies and ("PUT", f"/api/repos/{SLUG}/notifications") in bodies, "starring or marking read was not sent")
check(all(a in ("", "Bearer good-token", "Bearer wrong-token") for m, p, a, body in sent), "an unexpected Authorization header was sent")
check(not any(a and p.startswith("/login-site/") for m, p, a, body in sent), "the token was sent to the sign-in site")
check(value("DEVICE ") == "[] ABCD-1234 https://github.com/login/device 1", f"device flow start: {value('DEVICE ')}")
check(value("POLL1 ") == "pending" and value("POLL2 ") == "[] test-player", f"device flow polling: {value('POLL1 ')} {value('POLL2 ')}")
check(value("AFTER ") == "|false", "signing out leaves the token behind")

assert not problems, "\n".join(problems)
print(f"PASS repository status: {len(views)} views, signing in, and {len(expect)} account actions against a stand-in GitHub")
