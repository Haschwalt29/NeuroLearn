import subprocess
import tempfile
import os
import sys
import json
import shlex
from time import perf_counter

DEFAULT_TIMEOUT = 5
MAX_OUTPUT_BYTES = 200_000

class SandboxResult:
    def __init__(self, output: str, error: str, status: str, exec_ms: int):
        self.output = output
        self.error = error
        self.status = status
        self.exec_ms = exec_ms

def _truncate(data: bytes) -> str:
    if data is None:
        return ""
    s = data.decode("utf-8", errors="replace")
    if len(s) > MAX_OUTPUT_BYTES:
        return s[:MAX_OUTPUT_BYTES] + "\n... [truncated]"
    return s

def run_code(language: str, code: str, timeout: int = DEFAULT_TIMEOUT) -> SandboxResult:
    lang = (language or "").lower()
    start = perf_counter()
    try:
        if lang in ("python", "py"):
            return _run_local_python(code, timeout, start)
        if lang in ("javascript", "js"):
            return _run_local_node(code, timeout, start)
        return SandboxResult("", f"Unsupported language: {language}", "error", int((perf_counter()-start)*1000))
    except subprocess.TimeoutExpired:
        return SandboxResult("", "Execution timed out", "timeout", int((perf_counter()-start)*1000))
    except Exception as e:
        return SandboxResult("", str(e), "error", int((perf_counter()-start)*1000))

def _run_local_python(code: str, timeout: int, start: float) -> SandboxResult:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
        f.write(code)
        f.flush()
        path = f.name
    try:
        proc = subprocess.run([sys.executable, "-I", path], capture_output=True, timeout=timeout)
        out = _truncate(proc.stdout)
        err = _truncate(proc.stderr)
        status = "success" if proc.returncode == 0 else "error"
        return SandboxResult(out, err, status, int((perf_counter()-start)*1000))
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

def _run_local_node(code: str, timeout: int, start: float) -> SandboxResult:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mjs", mode="w", encoding="utf-8") as f:
        # Force strict mode and no require; node in module mode
        f.write("""// sandbox
import { setTimeout as delay } from 'node:timers/promises';
""")
        f.write("\n" + code)
        f.flush()
        path = f.name
    try:
        proc = subprocess.run(["node", "--no-warnings", "--experimental-global-webcrypto", path], capture_output=True, timeout=timeout)
        out = _truncate(proc.stdout)
        err = _truncate(proc.stderr)
        status = "success" if proc.returncode == 0 else "error"
        return SandboxResult(out, err, status, int((perf_counter()-start)*1000))
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


