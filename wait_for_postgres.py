import time
import psycopg2
import os
from urllib.parse import urlparse

MAX_RETRIES = 15
WAIT_SECONDS = 2

def wait_for_postgres():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("[SKIP] DATABASE_URL non definito, nessun wait necessario.")
        return

    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 5432
    user = parsed.username
    password = parsed.password
    dbname = parsed.path.lstrip("/")

    for i in range(MAX_RETRIES):
        try:
            print(f"[INFO] Tentativo {i+1}/{MAX_RETRIES}: connessione a {host}:{port}...")
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.close()
            print("[SUCCESS] PostgreSQL pronto.")
            return
        except psycopg2.OperationalError:
            print("[WAIT] PostgreSQL non ancora pronto, ritento tra 1s...")
            time.sleep(WAIT_SECONDS)

    raise RuntimeError("[ERROR] Impossibile connettersi a PostgreSQL dopo vari tentativi.")

if __name__ == "__main__":
    wait_for_postgres()
