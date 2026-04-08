import requests
import json

print("Testing direct SIMULATE endpoint...")
try:
    res = requests.post(
        "http://127.0.0.1:8000/simulate",
        json={
            "revenue": 5000,
            "users": 200,
            "cash": 8000,
            "burn_rate": 600,
            "expenses": 2500
        }
    )
    print("STATUS:", res.status_code)
    data = res.json()
    print("Keys returned:", data.keys())
    print("Graph cash over time:", data["graph"]["cash"])
except Exception as e:
    print("ERROR:", str(e))
