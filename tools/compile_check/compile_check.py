"""Compile the client and the server with NVGT on Linux, without Windows.

The game targets NVGT 0.90 on Windows. NVGT also publishes a Linux build
(https://nvgt.dev/downloads, nvgt_0.90.0_dev.tar.gz), which is older than
the one the game is built with and has no Windows-only plugins. This script
copies the working tree to a temporary folder, bridges those differences
there, and compiles both programs, so a missing function or a type error is
caught on any machine. Nothing in the working tree is changed.

The bridges, applied only to the temporary copy:
- nvgt_dev_stubs.nvgt declares the APIs the dev build lacks (process,
  game_window, text_font, newer key names, window size, application volume)
  and the Windows plugins' classes (notifications, voice commands). Their
  "#pragma plugin" lines are removed.
- The dev build has no #define, so the one include guard using it is
  dropped; NVGT includes each file only once anyway.
- The Linux curl plugin replaces the Windows DLLs in lib/.

Usage:
    python tools/compile_check/compile_check.py --nvgt /path/to/nvgt
    (or set NVGT to the nvgt executable)

Exit status 0 when both compile. With a current Windows-matching NVGT, pass
--no-stubs; the stubs would then clash with the real declarations.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WINDOWS_PLUGINS = ("notifications", "voice_command", "nvgt_app_volume")


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, check=True).stdout.decode()
    return [n for n in out.split("\0") if n and (ROOT / n).is_file()]


def prepare(work: Path, nvgt: Path, stubs: bool) -> None:
    for name in tracked_files():
        if name.endswith((".ogg", ".wav", ".exe", ".dll", ".map")) and not name.startswith("lib/"):
            continue
        target = work / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    if not stubs:
        return
    plugin = re.compile(r"^#pragma plugin (%s)\s*$" % "|".join(WINDOWS_PLUGINS), re.M)
    for path in (work / "includes").rglob("*.nvgt"):
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        new = plugin.sub("", text)
        if new != text:
            path.write_text(new, encoding="utf-8", errors="surrogateescape")
    shutil.copy2(HERE / "nvgt_dev_stubs.nvgt", work / "nvgt_dev_stubs.nvgt")
    main = work / "Infinite Warfare.nvgt"
    main.write_text('#include "nvgt_dev_stubs.nvgt"\n' + main.read_text(encoding="utf-8", errors="surrogateescape"),
                    encoding="utf-8", errors="surrogateescape")
    lib = work / "lib"
    lib.mkdir(exist_ok=True)
    for dll in lib.glob("*.dll"):
        dll.unlink()
    curl = nvgt.parent / "lib" / "libnvgt_curl.so"
    if curl.exists():
        shutil.copy2(curl, lib / "nvgt_curl.so")


def compile_one(nvgt: Path, work: Path, script: str) -> list[str]:
    folder = (work / script).parent
    result = subprocess.run([str(nvgt), "-c", "-p", "linux", (work / script).name], cwd=folder,
                            capture_output=True, text=True, timeout=1200)
    output = (result.stdout + result.stderr).replace(str(work) + os.sep, "")
    if result.returncode == 0:
        return []
    errors, lines = [], output.splitlines()
    for i, line in enumerate(lines):
        if "ERROR" in line:
            where = " ".join(l.strip() for l in lines[max(0, i - 2):i] if l.strip())
            errors.append(f"{where}: {line.strip()}")
    return errors or [output.strip()[-2000:]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nvgt", default=os.environ.get("NVGT", ""))
    parser.add_argument("--no-stubs", action="store_true")
    parser.add_argument("--only", choices=("client", "server"))
    args = parser.parse_args()
    nvgt = Path(args.nvgt) if args.nvgt else None
    if nvgt is None or not nvgt.exists():
        print("NVGT not found. Download nvgt_0.90.0_dev.tar.gz from https://nvgt.dev/downloads, "
              "unpack it, and pass --nvgt /path/to/nvgt or set NVGT.")
        return 2
    failed = False
    with tempfile.TemporaryDirectory(prefix="iw-compile-") as temp:
        work = Path(temp)
        prepare(work, nvgt.resolve(), not args.no_stubs)
        for label, script in (("client", "Infinite Warfare.nvgt"), ("server", "iwserver/iwserver.nvgt")):
            if args.only and args.only != label:
                continue
            errors = compile_one(nvgt.resolve(), work, script)
            if errors:
                failed = True
                print(f"FAIL {label}: {len(errors)} errors")
                for e in errors:
                    print("  " + e)
            else:
                print(f"PASS {label} compiles")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
