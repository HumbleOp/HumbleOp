# test_auth.py

import sys
import requests

BASE_URL = "http://127.0.0.1:5000"

def pretty_print(resp):
    print(f"\n→ {resp.request.method} {resp.url}")
    print(f"Status: {resp.status_code}")
    try:
        print("Body:", resp.json())
    except ValueError:
        print("Body:", resp.text)

def test_register(username, password):
    resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password}
    )
    pretty_print(resp)
    return resp

def test_login(username, password):
    resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password}
    )
    pretty_print(resp)
    if resp.status_code == 200:
        return resp.json().get("token")
    return None

def test_profile_no_token():
    resp = requests.get(f"{BASE_URL}/profile")
    pretty_print(resp)

def test_profile_with_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/profile", headers=headers)
    pretty_print(resp)

if __name__ == "__main__":
    # 1) REGISTER Alice
    print("== REGISTER Alice ==")
    test_register("alice", "AlicePass123")
    # 1.1) Attempt duplicate register
    print("== REGISTER Alice again ==")
    test_register("alice", "AlicePass123")

    # 2) LOGIN Alice
    print("== LOGIN Alice ==")
    alice_token = test_login("alice", "AlicePass123")
    if not alice_token:
        print("🔴 Login failed for alice")
        sys.exit(1)

    # 3) TEST PROFILE
    print("\n== PROFILE without token ==")
    test_profile_no_token()

    print("\n== PROFILE with token ==")
    test_profile_with_token(alice_token)

    print("\n✔️ All auth tests executed.")
