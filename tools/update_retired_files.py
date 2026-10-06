"""Write updater/retired_files.txt: files the game once shipped and no longer does.

The updater deletes these from an installation, and the client deletes them
once after each new build starts, so a weapon or item that was removed or
moved stops being loaded from a stale copy. The list comes from the
repository's history: every path ever deleted that does not exist now.

Only the game's own folders are listed. Server accounts, logs and other
runtime data are never listed, and neither is the old "source/" snapshot
folder, which players may have reused for their own files.

Run it after deleting or moving any shipped file, before committing:

    python tools/update_retired_files.py

It needs the full history; in a shallow clone run "git fetch --unshallow".
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "updater" / "retired_files.txt"
GAME_FOLDERS = ("includes/", "iwserver/content/", "iwserver/docs/", "iwserver/includes/",
                "iwserver/physics_maps/", "lib/", "sounds/", "tools/", "updater/")
RUNTIME = ("/accounts/", "/administration/", "logs/", ".svr", "admins.txt", "currentmap.txt")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def retired_paths() -> list[str]:
    if git("rev-parse", "--is-shallow-repository").strip() == "true":
        raise SystemExit("This clone is shallow; run git fetch --unshallow first.")
    deleted = set(git("log", "-z", "--no-renames", "--diff-filter=D", "--name-only", "--format=", "HEAD").replace("\n", "\0").split("\0"))
    # Deletions staged for the commit being prepared count too.
    deleted |= set(git("diff", "-z", "--cached", "--no-renames", "--diff-filter=D", "--name-only").split("\0"))
    current = set(git("ls-files", "-z").split("\0"))
    return sorted(p for p in deleted - current
                  if p and p.startswith(GAME_FOLDERS) and not any(r in p for r in RUNTIME))


def render(paths: list[str]) -> str:
    return "\n".join(paths) + "\n"


if __name__ == "__main__":
    text = render(retired_paths())
    if "--check" in sys.argv:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            raise SystemExit("updater/retired_files.txt is out of date; run python tools/update_retired_files.py")
        print("PASS retired files list is current")
    else:
        OUTPUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {OUTPUT.relative_to(ROOT)} with {text.count(chr(10))} paths")
