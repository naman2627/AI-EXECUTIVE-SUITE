import requests

print("Testing direct STRATEGY endpoint...")
try:
    res = requests.post(
        "http://127.0.0.1:8000/strategy",
        json={
            "role": "CEO",
            "problem": "We need to expand into Europe."
        }
    )
    print("STATUS:", res.status_code)
    print("RESPONSE:", res.json())
except Exception as e:
    print("ERROR:", str(e))
