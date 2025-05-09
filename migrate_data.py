# migrate_data.py
import json
import os
import sys

# Metti la cartella corrente nel path così che possa importare HumbleCore.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importa la tua app e i modelli
import HumbleCore as core
app      = core.app
db       = core.db
User     = core.User
Post     = core.Post
Comment  = core.Comment
Vote     = core.Vote
Flag     = core.Flag
Like     = core.Like
Badge    = core.Badge

def migrate():
    # 1) Carica gli utenti + i loro badge
    with open("users.json", "r") as f:
        users_json = json.load(f)

    for uname, u in users_json.items():
        user = User(
            username      = uname,
            password_hash = u.get("password_hash"),
            token         = u.get("token"),
            avatar_url    = u.get("avatar_url", ""),
            bio           = u.get("bio", "")
        )
        db.session.add(user)
        for badge_name in u.get("badges", []):
            db.session.add(Badge(user=uname, name=badge_name))
    db.session.commit()

    # 2) Migra i follows (many-to-many)
    for uname, u in users_json.items():
        me = User.query.get(uname)
        for other in u.get("following", []):
            target = User.query.get(other)
            if target:
                me.following.append(target)
    db.session.commit()

    # 3) Carica i post + commenti, vote, flag, like
    with open("data.json", "r") as f:
        posts_json = json.load(f)

    for pid, p in posts_json.items():
        post = Post(
            id        = pid,
            author    = p["author"],
            body      = p["body"],
            started   = p.get("started", False),
            postponed = p.get("postponed", False),
            winner    = p.get("winner"),
            second    = p.get("second")
        )
        db.session.add(post)

        # Commenti
        for c in p.get("comments", {}).values():
            db.session.add(Comment(
                post_id   = pid,
                commenter = c["commenter"],
                text      = c["text"]
            ))

        # Voti (uno per ogni conteggio)
        for voter, count in p.get("votes", {}).items():
            for _ in range(count):
                db.session.add(Vote(post_id=pid, voter=voter, candidate=voter))

        # Flags e Likes
        for f_user in p.get("flags", []):
            db.session.add(Flag(post_id=pid, flagger=f_user))
        for l_user in p.get("likes", []):
            db.session.add(Like(post_id=pid, liker=l_user))

    db.session.commit()
    print("🎉 Migrazione completata!")

if __name__ == "__main__":
    # Attiva il contesto Flask
    with app.app_context():
        migrate()
