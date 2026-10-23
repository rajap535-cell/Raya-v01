"""
RAYA - Runtime Proof scaffolding (shared by every STEP script).

Every STEP script boots the REAL application script
``raya_farmer_interface.py`` inside a REAL Streamlit runtime
(``streamlit.testing.v1.AppTest`` -> real ScriptRunner, real widget states,
real session_state, real ``st.rerun()`` handling) and drives it ONLY through
rendered widgets, the same way a user would.

Nothing here bypasses the UI to write data. Persistence happens because a
widget click made the app call the real backend singletons, which wrote the
real JSON files under ``data/persistent_memory``.

Instrumentation: ``install_search_instrumentation()`` wraps
``farmer_search_engine.farmer_search`` BEFORE the app (and therefore
``persistent_pipeline`` / ``contextual_decision_engine``) is imported, so every
module that binds the symbol receives the counting wrapper. Each invocation is
appended to ``runtime_proof/out/farmer_search_calls.jsonl`` with its caller
stack, proving how many times it ran and from where.
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
PROOF_DIR = Path(__file__).resolve().parent
OUT_DIR = PROOF_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

APP_PATH = BASE_DIR / "raya_farmer_interface.py"
DATA_DIR = BASE_DIR / "data" / "persistent_memory"
CALL_LOG = OUT_DIR / "farmer_search_calls.jsonl"
STATE_FILE = OUT_DIR / "state.json"

RUN_LABEL = os.environ.get("RAYA_RUN_LABEL", "unlabelled-run")

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def say(message: str = "") -> None:
    """Console-safe print (ASCII, so PowerShell never mangles evidence)."""
    text = str(message)
    try:
        sys.stdout.write(text.encode("ascii", "backslashreplace").decode("ascii"))
    except Exception:
        sys.stdout.write(repr(text))
    sys.stdout.write("\n")
    sys.stdout.flush()


def banner(title: str) -> None:
    say("")
    say("=" * 74)
    say(f"  {title}")
    say("=" * 74)


# ============================================================
# 1. farmer_search() CALL INSTRUMENTATION
# ============================================================

_CALLS: List[Dict[str, Any]] = []
_INSTALLED = False


def install_search_instrumentation() -> None:
    """Wrap farmer_search() with a call recorder. Must run before app import."""

    global _INSTALLED

    if _INSTALLED:
        return

    import farmer_search_engine as engine_module

    original = engine_module.farmer_search

    if getattr(original, "_raya_instrumented", False):
        _INSTALLED = True
        return

    def counting_farmer_search(*args, **kwargs):

        record = {
            "call_index_in_process": len(_CALLS) + 1,
            "run_label": RUN_LABEL,
            "pid": os.getpid(),
            "wall_clock": time.strftime("%Y-%m-%d %H:%M:%S"),
            "args": [str(a) for a in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()},
            "called_from": [
                f"{Path(f.filename).name}:{f.lineno} in {f.name}"
                for f in traceback.extract_stack()[:-1]
                if "farmer_search_engine.py" not in Path(f.filename).name
            ][:6],
        }

        _CALLS.append(record)

        with open(CALL_LOG, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        say(f"    [FARMER_SEARCH CALL #{len(_CALLS)}] kwargs={record['kwargs']}")
        say(f"        from <- {' <- '.join(record['called_from'][:3])}")

        return original(*args, **kwargs)

    counting_farmer_search._raya_instrumented = True
    counting_farmer_search._raya_original = original

    engine_module.farmer_search = counting_farmer_search

    _INSTALLED = True
    say(f"[instrument] farmer_search() wrapped - run='{RUN_LABEL}' pid={os.getpid()}")


def search_call_count() -> int:
    return len(_CALLS)


def search_calls_between(before: int, after: int) -> List[Dict[str, Any]]:
    return _CALLS[before:after]
