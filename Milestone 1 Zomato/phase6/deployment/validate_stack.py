"""Stack validation script: verify all services are up and responding correctly."""

from __future__ import annotations

import json
import sys
import urllib.request


BACKEND = "http://localhost:8000"
FRONTEND = "http://localhost:3000"


def _fetch(url: str, timeout: int = 10) -> tuple[int, str]:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except Exception as exc:
        return 0, str(exc)


def validate_backend() -> bool:
    """Validate backend health, locations, and cuisines endpoints."""
    print("Validating backend...")

    # Health
    status, body = _fetch(f"{BACKEND}/api/v1/health")
    if status != 200:
        print(f"  FAIL: /api/v1/health returned {status}")
        return False
    health = json.loads(body)
    if health.get("status") != "ok":
        print(f"  FAIL: health status is {health}")
        return False
    print("  /api/v1/health: OK")

    # Locations
    status, body = _fetch(f"{BACKEND}/api/v1/locations")
    if status != 200:
        print(f"  FAIL: /api/v1/locations returned {status}")
        return False
    locations = json.loads(body).get("locations", [])
    print(f"  /api/v1/locations: OK ({len(locations)} locations)")

    # Cuisines
    status, body = _fetch(f"{BACKEND}/api/v1/cuisines")
    if status != 200:
        print(f"  FAIL: /api/v1/cuisines returned {status}")
        return False
    cuisines = json.loads(body).get("cuisines", [])
    print(f"  /api/v1/cuisines: OK ({len(cuisines)} cuisines)")

    return True


def validate_frontend() -> bool:
    """Validate frontend is serving HTML."""
    print("Validating frontend...")
    status, body = _fetch(FRONTEND)
    if status != 200 or "<!DOCTYPE html>" not in body[:200].upper():
        print(f"  FAIL: frontend returned status {status}")
        return False
    print(f"  {FRONTEND}: OK")
    return True


def validate_recommendation() -> bool:
    """Validate recommendation endpoint returns valid results."""
    print("Validating recommendation endpoint...")
    payload = json.dumps({
        "location": "Bellandur",
        "budget": "high",
        "cuisine": "",
        "min_rating": 4.0,
    }).encode()

    req = urllib.request.Request(
        f"{BACKEND}/api/v1/recommendations",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        print(f"  FAIL: recommendation request failed: {exc}")
        return False

    recs = data.get("recommendations", [])
    if not recs:
        print("  FAIL: no recommendations returned")
        return False

    print(f"  Recommendations: OK ({len(recs)} results)")
    for r in recs[:3]:
        name = r.get("restaurant", {}).get("name", "?")
        rating = r.get("restaurant", {}).get("rating", "?")
        print(f"    #{r.get('rank')} {name} (rating: {rating})")

    return True


def main() -> int:
    checks = [
        ("Backend", validate_backend),
        ("Frontend", validate_frontend),
        ("Recommendation", validate_recommendation),
    ]

    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as exc:
            print(f"  ERROR: {name} check raised {exc}")
            results[name] = False

    print("\n" + "=" * 40)
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
