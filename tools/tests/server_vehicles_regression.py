"""Server vehicles, run in the real server code with NVGT.

Builds a copy of the server whose main() is server_vehicles_regression.nvgt's
(the server's own main() is renamed), then runs it from the copy's iwserver
folder so it finds its maps and content. Needs NVGT (set NVGT to the
executable); without it, it reports a skip.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
nvgt = os.environ.get("NVGT") or shutil.which("nvgt")
if not nvgt:
    print("SKIP server vehicles: set NVGT to an NVGT executable to run it")
    sys.exit(0)

with tempfile.TemporaryDirectory(prefix="iw-server-vehicles-") as temp:
    work = Path(temp)
    shutil.copytree(ROOT / "iwserver", work / "iwserver", ignore=shutil.ignore_patterns("accounts", "*.log"))
    shutil.copytree(ROOT / "includes", work / "includes")
    server = work / "iwserver" / "iwserver.nvgt"
    text = server.read_text(encoding="utf-8")
    text = re.sub(r"^#define .*$", "", text, flags=re.M)
    text = text.replace("\nvoid main()\n", "\nvoid server_main()\n", 1)
    text += "\n" + (ROOT / "tools/tests/server_vehicles_regression.nvgt").read_text(encoding="utf-8")
    stubs = ROOT / "tools/compile_check/nvgt_dev_stubs.nvgt"
    shutil.copy2(stubs, work / "iwserver" / "nvgt_dev_stubs.nvgt")
    runner = work / "iwserver" / "server_vehicles_runner.nvgt"
    runner.write_text(text, encoding="utf-8")
    (work / "iwserver" / "administration").mkdir(exist_ok=True)
    result = subprocess.run([nvgt, runner.name], cwd=work / "iwserver", capture_output=True, text=True, timeout=600)
    if "Compilation error" in result.stdout + result.stderr:
        runner.write_text('#include "nvgt_dev_stubs.nvgt"\n' + text, encoding="utf-8")
        result = subprocess.run([nvgt, runner.name], cwd=work / "iwserver", capture_output=True, text=True, timeout=600)
    report = work / "iwserver" / "administration" / "server_vehicles_regression.txt"
    output = report.read_text(encoding="utf-8") if report.exists() else ""
    if os.environ.get("IW_SHOW") or "FAIL" in output or not output:
        print(output or (result.stdout[-4000:] + result.stderr[-4000:]))
    if not output:
        raise SystemExit("server_vehicles_regression.nvgt did not run")
    failures = [line for line in output.splitlines() if line.startswith("FAIL")]
    assert not failures, "\n".join(failures)
    print(f"PASS server vehicles: {output.count('PASS ')} checks")
