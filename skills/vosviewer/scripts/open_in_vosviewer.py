"""
Open a VOSviewer JSON in VOSviewer Online (via ?json= URL) or the desktop app.

Usage:
    # Build the Online URL from a public JSON URL
    python open_in_vosviewer.py --json-url https://example.com/map.json

    # Open local file in desktop VOSviewer (requires VOSviewer.jar on PATH or --jar)
    python open_in_vosviewer.py --local map.json --desktop --jar "C:/apps/VOSviewer/VOSviewer.jar"

    # Print the raw Online URL without opening
    python open_in_vosviewer.py --json-url https://... --print-only
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import urllib.parse
import webbrowser
from pathlib import Path


def online_url(json_url: str) -> str:
    return f"https://app.vosviewer.com/?json={urllib.parse.quote(json_url, safe='')}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-url", help="Public HTTPS URL to a VOSviewer JSON file")
    ap.add_argument("--local", help="Path to a local VOSviewer JSON file")
    ap.add_argument("--desktop", action="store_true", help="Open in desktop VOSviewer")
    ap.add_argument("--jar", default="", help="Path to VOSviewer.jar (desktop mode)")
    ap.add_argument("--print-only", action="store_true", help="Only print URL/command")
    args = ap.parse_args()

    if args.desktop:
        if not args.local:
            sys.exit("--desktop requer --local <json file>")
        jar = args.jar or "VOSviewer.jar"
        cmd = ["java", "-jar", jar, "--json", str(Path(args.local).resolve())]
        print("Run:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
        if not args.print_only:
            subprocess.Popen(cmd)
        return

    if not args.json_url:
        sys.exit("Informe --json-url (URL pública HTTPS).")

    url = online_url(args.json_url)
    print(url)
    if not args.print_only:
        webbrowser.open(url)


if __name__ == "__main__":
    main()
