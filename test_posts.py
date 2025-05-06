# test_posts.py

import sys
import requests

BASE = "http://127.0.0.1:5000"

def pretty(resp):
    print(f"\n→ {resp.request.method} {resp.url}")
    print("Status:", resp.status_code)
    try:
        print("Body:", resp.json())
    except:
        print("Body:", resp.text)

def login(username, password):
    r = requests.post(f"{BASE}/login", json={"username":username, "password":password})
    pretty(r)
    if r.status_code == 200:
        return r.json()["token"]
    sys.exit(f"Login failed for {username}")

if __name__=="__main__":
    # 1) login Alice & Bob (già registrati)
    alice_token = login("alice", "AlicePass123")
    bob_token   = login("bob",   "BobPass123")

    headers_alice = {"Authorization": f"Bearer {alice_token}"}
    headers_bob   = {"Authorization": f"Bearer {bob_token}"}

    # 2) Create post1 as Alice
    r = requests.post(f"{BASE}/create_post/post1",
        headers={**headers_alice, "Content-Type":"application/json"},
        json={"body":"Hello, HumbleOp world!"})
    pretty(r)

    # 3) Bob comments
    r = requests.post(f"{BASE}/comment/post1",
        headers={**headers_bob, "Content-Type":"application/json"},
        json={"text":"My first comment!"})
    pretty(r)

    # 4) List comments
    r = requests.get(f"{BASE}/comments/post1", headers=headers_alice)
    pretty(r)

    # 5) Alice votes Bob
    r = requests.post(f"{BASE}/vote/post1",
        headers={**headers_alice, "Content-Type":"application/json"},
        json={"candidate":"bob"})
    pretty(r)

    # 6) Get results
    r = requests.get(f"{BASE}/results/post1")
    pretty(r)

    print("\n✔️ All post/comment/vote tests done.")
