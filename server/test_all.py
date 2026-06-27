"""
Test all endpoints
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("\n✅ Testing GET /health")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

def test_system_status():
    print("\n✅ Testing GET /system/status")
    r = requests.get(f"{BASE_URL}/system/status")
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

def test_documents_status():
    print("\n✅ Testing GET /documents/status")
    r = requests.get(f"{BASE_URL}/documents/status")
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

def test_chat():
    print("\n✅ Testing POST /chat/")
    data = {
        "query": "O que é VertexCode?",
        "session_id": "test_user"
    }
    r = requests.post(f"{BASE_URL}/chat/", json=data)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Error: {r.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing all endpoints")
    print("=" * 60)

    try:
        test_health()
        test_system_status()
        test_documents_status()
        time.sleep(2)
        test_chat()
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
