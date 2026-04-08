import requests
import time

print("Testing direct endpoint...")
try:
    res = requests.post(
        "http://127.0.0.1:8000/chat",
        json={
            "message": "hello",
            "role": "CEO",
            "history": []
        }
    )
    print("STATUS:", res.status_code)
    print("JSON:", res.json())
except Exception as e:
    print("ERROR:", str(e))
