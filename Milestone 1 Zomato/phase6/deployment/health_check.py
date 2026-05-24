"""Standalone health check script for deployment validation."""

from __future__ import annotations

import sys
import urllib.request
import json


DEFAULT_URL = "http://localhost:8000/api/v1/health"


def check_health(url: str = DEFAULT_URL) -> bool:
    """Check if the backend health endpoint responds with status ok."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("status") == "ok"
    except Exception as exc:
        print(f"Health check FAILED: {exc}", file=sys.stderr)
        return False


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Health check for Zomato Recommender backend")
    parser.add_argument("--url", default=DEFAULT_URL, help="Health endpoint URL")
    args = parser.parse_args()

    if check_health(args.url):
        print("Health check PASSED")
        return 0
    else:
        print("Health check FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
