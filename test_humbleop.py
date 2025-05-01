import requests
import time

BASE_URL = "http://127.0.0.1:5000"
POST_ID = "post123"

def start_duel():
    print("🔹 Sending POST to /start_duel...")
    response = requests.post(
        f"{BASE_URL}/start_duel/{POST_ID}",
        json={"winner": "Alice", "second": "Bob"}
    )
    print("➤ Response:", response.json())

def check_status():
    print("🔹 Checking status...")
    response = requests.get(f"{BASE_URL}/status/{POST_ID}")
    try:
        data = response.json()
    except:
        data = response.text
    print("➤ Status:", data)

def start_now():
    print("🔹 Sending POST to /start_now...")
    response = requests.post(f"{BASE_URL}/start_now/{POST_ID}")
    print("➤ Response:", response.json())

if __name__ == "__main__":
    print("=== TEST HumbleOp ===")
    start_duel()
    time.sleep(1)  # aspetta un secondo
    check_status()
    
    input("\nPremi INVIO per simulare che Alice inizi il duello...")
    start_now()
    check_status()
