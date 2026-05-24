"""Launch UI: python -m ui  |  python -m ui --cli"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    if "--cli" in sys.argv:
        from ui.phase2.cli import main as cli_main

        raise SystemExit(cli_main([a for a in sys.argv[1:] if a != "--cli"]))

    app_path = Path(__file__).resolve().parent / "phase2" / "streamlit_app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless",
        "true",
    ]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
