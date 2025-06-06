# scripts/retroactive.py

from datetime import datetime
from core.extensions import db
from models import Post
from app import create_app

def retroattiva_imposta_started():
    now = datetime.utcnow()
    # Trova tutti i post la cui voting_deadline è già scaduta e che hanno started=False
    posts_da_aggiornare = (
        db.session.query(Post)
        .filter(Post.voting_deadline <= now)
        .filter(Post.started == False)
        .all()
    )

    for post in posts_da_aggiornare:
        post.started = True

    db.session.commit()
    print(f"Aggiornati {len(posts_da_aggiornare)} post già scaduti.")

if __name__ == "__main__":
    # Creo l'app e entro nell'app_context
    app = create_app()
    with app.app_context():
        retroattiva_imposta_started()
