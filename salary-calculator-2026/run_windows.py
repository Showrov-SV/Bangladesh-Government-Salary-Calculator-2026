"""
Windows launcher for the Salary Calculator app.

Why this exists:
Streamlit's dev server (Tornado) can hit a known Windows-only bug where the
ProactorEventLoop throws `ConnectionResetError: [WinError 10054]` when a
browser connection is closed/reopened quickly (e.g. clicking "Download PDF"
twice in a row). This can corrupt the second download, since the response
gets cut off before the filename header is sent - the browser then saves
the raw file under Streamlit's internal media hash name instead.

Switching to the SelectorEventLoop policy avoids this. It must be set
BEFORE Streamlit creates its own event loop, so it has to happen in a
separate launcher script rather than inside app.py.

Usage (from the project folder, with your venv activated):
    python run_windows.py
"""
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from streamlit.web import cli as stcli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())
