"""Quick live test of the FastAPI backend recommendation endpoint."""
import urllib.request
import json

payload = json.dumps({
    "location": "Bellandur",
    "budget": "high",
    "cuisine": "",
    "min_rating": 4.0,
}).encode()

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/recommendations",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

r = urllib.request.urlopen(req, timeout=30)
data = json.loads(r.read())

print(f"Status: 200 OK")
print(f"Recommendations returned: {len(data['recommendations'])}")
print()
for rec in data["recommendations"]:
    rest = rec["restaurant"]
    print(f"  #{rec['rank']}  {rest['name']}")
    print(f"       Rating: {rest['rating']}  |  Cost for 2: Rs.{rest.get('cost_for_two', 'N/A')}")
    print(f"       Cuisines: {rest.get('cuisines', 'N/A')}")
    print(f"       Explanation: {rec['explanation'][:100]}...")
    print()

summary = data.get("overall_summary") or ""
print(f"Overall summary ({len(summary)} chars):")
print(summary[:300])
