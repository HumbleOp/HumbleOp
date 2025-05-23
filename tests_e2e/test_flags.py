def test_flag_switches_winner_if_threshold_met(client, unique_post_id, alice_token):
    pid = unique_post_id

    # Alice crea post e commenta
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Flag this"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "Commento"})

    # Bob come secondo partecipante
    uname = "flag_bob"
    client.post("/register", json={"username": uname, "password": "p", "email": f"{uname}@example.com"})
    bob_token = client.post("/login", json={"username": uname, "password": "p"}).json()["token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"text": "Risposta"})

    # Entrambi votano (Alice vince, Bob è secondo)
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"candidate": "alice"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "flag_bob"})

    # Utente terzo vota per Bob, così diventa effettivamente secondo
    client.post("/register", json={"username": "userX", "password": "p", "email": "userX@example.com"})
    userX_token = client.post("/login", json={"username": "userX", "password": "p"}).json()["token"]
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {userX_token}"}, json={"candidate": "flag_bob"})

    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {alice_token}"})

    # Un like minimo
    client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {alice_token}"})

    # Ora arrivano 10 flag da utenti diversi (rapporto flag/(flag+like) = 10/11 > 0.6)
    for i in range(10):
        uname = f"flagger{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        token = client.post("/login", json={"username": uname, "password": "x"}).json()["token"]
        client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {token}"})

    # Controlla che ora il vincitore sia cambiato da Alice a Bob
    res = client.get(f"/status/{pid}").json()
    assert res["winner"] == "flag_bob"
    assert res["postponed"] is False
    assert res["started"] is False

    # Verifica /results riflette lo switch
    results = client.get(f"/results/{pid}").json()
    assert results["winner"] == "flag_bob"
    assert "ranking" in results
    assert results["ranking"].get("flag_bob", 0) >= 1


    # Verifica /profile contiene dati sensati per Alice
    profile = client.get("/profile", headers={"Authorization": f"Bearer {alice_token}"}).json()
    assert "badges" in profile
    assert "First blood" in profile["badges"]
    assert "username" in profile and profile["username"] == "alice"

def test_flag_does_not_switch_if_threshold_not_met(client, unique_post_id, alice_token):
    pid = unique_post_id

    # Alice crea post e commenta
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Safe post"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"text": "Commento"})

    # Bob come secondo partecipante
    uname = "safe_bob"
    client.post("/register", json={"username": uname, "password": "p", "email": f"{uname}@example.com"})
    bob_token = client.post("/login", json={"username": uname, "password": "p"}).json()["token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"text": "Risposta"})

    # Entrambi votano (Alice vince, Bob è secondo)
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"candidate": "alice"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {bob_token}"}, json={"candidate": "safe_bob"})

    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {alice_token}"})

    # 3 like, 2 flag = 2/5 = 0.4 → non basta per lo switch
    for i in range(3):
        uname = f"liker{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        token = client.post("/login", json={"username": uname, "password": "x"}).json()["token"]
        client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {token}"})

    for i in range(2):
        uname = f"flaggerx{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        token = client.post("/login", json={"username": uname, "password": "x"}).json()["token"]
        client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {token}"})

    # Controlla che Alice rimanga vincitrice
    res = client.get(f"/status/{pid}").json()
    assert res["winner"] == "alice"
    assert res["postponed"] is False
    assert res["started"] is False

    # /results conferma che il vincitore non è cambiato
    results = client.get(f"/results/{pid}").json()
    assert results["winner"] == "alice"
    assert "ranking" in results
    assert results["ranking"].get("alice", 0) >= 1

