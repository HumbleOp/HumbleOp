# test_auth.py (estensione)
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
    resp = requests.post(f"{BASE_URL}/register", json={"username":username,"password":password})
    pretty_print(resp)
    return resp

def test_login(username, password):
    resp = requests.post(f"{BASE_URL}/login",    json={"username":username,"password":password})
    pretty_print(resp)
    if resp.status_code == 200:
        return resp.json().get("token")
    return None

def test_profile(token):
    # senza token
    resp = requests.get(f"{BASE_URL}/profile")
    pretty_print(resp)
    # con token
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/profile", headers=headers)
    pretty_print(resp)

if __name__ == "__main__":
    # prima registro alice
    print("== REGISTER alice ==")
    test_register("alice", "AlicePass123")

    # poi registro bob
    print("== REGISTER bob ==")
    test_register("bob", "BobPass123")

    # login di alice
    print("== LOGIN alice ==")
    alice_token = test_login("alice", "AlicePass123")
    if not alice_token:
        print("🔴 login failed for alice")
        exit(1)

    # login di bob (se vuoi testarlo)
    print("== LOGIN bob ==")
    bob_token = test_login("bob", "BobPass123")

    # testa /profile
    print("== PROFILE ==")
    test_profile(alice_token)

    print("\n✔️ Profile tests done.")
