import time
import requests

API = "http://localhost:5000"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {token}"
}

def register_and_login(username, password="test123", email=None):
    email = email or f"{username}@example.com"
    requests.post(f"{API}/register", json={"username": username, "password": password, "email": email})
    r = requests.post(f"{API}/login", json={"username": username, "password": password})
    token = r.json().get("token")
    return token

def test_full_duel():
    post_id = "duel-test-001"

    # Step 1: Create users
    token_francesco = register_and_login("francesco")
    token_alessio = register_and_login("alessio")
    token_giulia = register_and_login("giulia")

    # Step 2: Francesco crea il post
    r = requests.post(
        f"{API}/create_post/{post_id}",
        headers={"Authorization": f"Bearer {token_francesco}"},
        json={"body": "#Test Duel Challenge", "voting_hours": 0.001}  # ~3.6 sec
    )
    print("Post creato:", r.json())

    # Step 3: Alessio e Giulia commentano
    requests.post(
        f"{API}/comment/{post_id}",
        headers={"Authorization": f"Bearer {token_alessio}"},
        json={"text": "Sono il migliore!"}
    )
    requests.post(
        f"{API}/comment/{post_id}",
        headers={"Authorization": f"Bearer {token_giulia}"},
        json={"text": "Io sono ancora meglio."}
    )

    # Step 4: Francesco vota Alessio
    requests.post(
        f"{API}/vote/{post_id}",
        headers={"Authorization": f"Bearer {token_francesco}"},
        json={"candidate": "alessio"}
    )

    # Step 5: attendi che voting_deadline passi
    print("[Attendo scadenza fase di voto...]")
    time.sleep(5)

    # Step 6: Alessio pianifica l'inizio del duello
    r = requests.post(
        f"{API}/schedule_duel/{post_id}",
        headers={"Authorization": f"Bearer {token_alessio}"},
        json={"start_in_hours": 0.001}  # ~3.6 sec
    )
    print("Duello pianificato:", r.json())

    # Step 7: attendi che inizi il duello
    print("[Attendo inizio duello...]")
    time.sleep(5)

    # Step 8: Giulia manda red flag contro Alessio
    r = requests.post(
        f"{API}/flag/{post_id}",
        headers={"Authorization": f"Bearer {token_giulia}"},
    )
    print("Red flag:", r.json())

if __name__ == "__main__":
    test_full_duel()
