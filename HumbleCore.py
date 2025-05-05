import json
import os
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

DATA_FILE = "data.json"

# Load data from JSON file (if exists)
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        posts = json.load(f)
else:
    posts = {}

def save_data():
    """Save the in-memory posts dict to disk."""
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=2)
    print("[DATA SAVED]")

def handle_duel_timeout(post_id):
    """Handle duel timeout: postpone once, then switch to second."""
    post = posts.get(post_id)
    if not post or post.get("started"):
        return

    if not post.get("postponed"):
        post["postponed"] = True
        scheduler.add_job(
            handle_duel_timeout,
            'date',
            run_date=datetime.now() + timedelta(hours=6),
            args=[post_id]
        )
    else:
        post["winner"] = post.get("second")
        post["postponed"] = False
        post["started"] = False
        scheduler.add_job(
            handle_duel_timeout,
            'date',
            run_date=datetime.now() + timedelta(hours=2),
            args=[post_id]
        )

    save_data()

@app.route("/create_post/<post_id>", methods=["POST"])
def create_post(post_id):
    data   = request.json
    author = data.get("author")
    body   = data.get("body")

    if not author or not body:
        return jsonify({"error": "Fields 'author' and 'body' are required."}), 400

    posts[post_id] = {
        "author": author,
        "body":   body,
        "comments": {},      # commenter -> text
        "commenters": [],    # who has già commentato
        "votes": {},         # votes per commenter
        "voted_users": [],   # chi ha già votato
        "flags": [],         # flag sul vincitore
        "likes": []          # like sul vincitore
        # winner/second saranno calcolati solo quando serve
    }
    save_data()
    return jsonify({"status": "Post created."}), 200

@app.route("/start_duel/<post_id>", methods=["POST"])
def start_duel(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    # devo avere almeno 1 commento per poter votare
    if len(post["commenters"]) < 1:
        return jsonify({"error": "Not enough comments to start duel."}), 400

    # calcolo winner e second in base ai voti
    ranking = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    winner = ranking[0][0]
    second = ranking[1][0] if len(ranking) > 1 else None

    # salvo e schedule
    post["winner"] = winner
    post["second"] = second
    post["postponed"] = False
    post["started"]   = False

    scheduler.add_job(
        handle_duel_timeout,
        'date',
        run_date=datetime.now() + timedelta(hours=2),
        args=[post_id]
    )
    save_data()
    return jsonify({
        "status": "Duel started.",
        "winner": winner,
        "second": second
    }), 200

@app.route("/start_now/<post_id>", methods=["POST"])
def user_started(post_id):
    """Manually mark the duel as started by the winner."""
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    post["started"] = True
    save_data()
    return jsonify({"status": "Duel started."}), 200

@app.route("/comment/<post_id>", methods=["POST"])
def add_comment(post_id):
    """Add a comment under a post (one comment per user)."""
    data = request.json
    commenter = data.get("commenter")
    text = data.get("text")
    post = posts.get(post_id)

    if not post:
        return jsonify({"error": "Post not found."}), 404
    if not commenter or not text:
        return jsonify({"error": "Both 'commenter' and 'text' are required."}), 400
    if commenter in post["commenters"]:
        return jsonify({"error": f"User '{commenter}' has already commented."}), 403

    post["comments"][commenter] = text
    post["commenters"].append(commenter)
    save_data()
    return jsonify({
        "status": "Comment added.",
        "comment": {"commenter": commenter, "text": text}
    }), 200

@app.route("/comments/<post_id>", methods=["GET"])
def get_comments(post_id):
    """List all comments for a post, with current vote counts."""
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    comments = []
    for c in post["commenters"]:
        comments.append({
            "commenter": c,
            "text": post["comments"][c],
            "votes": post["votes"].get(c, 0)
        })
    return jsonify({"comments": comments}), 200

@app.route("/vote/<post_id>", methods=["POST"])
def vote(post_id):
    """Vote for a specific comment on a post; one vote per user."""
    data = request.json
    voter = data.get("voter")
    candidate = data.get("candidate")

    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    if candidate not in post["commenters"]:
        return jsonify({"error": f"Candidate '{candidate}' has not commented."}), 400
    if voter in post["voted_users"]:
        return jsonify({"error": f"User '{voter}' has already voted."}), 403

    post["votes"][candidate] = post["votes"].get(candidate, 0) + 1
    post["voted_users"].append(voter)

    sorted_votes = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    post["winner"] = sorted_votes[0][0] if sorted_votes else None
    post["second"] = sorted_votes[1][0] if len(sorted_votes) > 1 else None

    save_data()
    return jsonify({
        "message": f"{voter} voted for {candidate}",
        "votes": post["votes"]
    }), 200

@app.route("/flag/<post_id>", methods=["POST"])
def flag_post(post_id):
    """
    Flag the current duel winner.
    Flags can be offset by likes 1:1.
    If net flags ≥ 40% of the winner’s original likes, switch to second place.
    """
    data = request.json
    flagger = data.get("user")
    post = posts.get(post_id)

    if not post:
        return jsonify({"error": "Post not found."}), 404

    winner = post.get("winner")
    if not winner:
        return jsonify({"error": "No winner to flag."}), 400

    # initialize flags and likes lists if missing
    post.setdefault("flags", [])
    post.setdefault("likes", [])

    # only one flag per user
    if flagger in post["flags"]:
        return jsonify({"error": f"User '{flagger}' has already flagged the winner."}), 403

    # register the flag
    post["flags"].append(flagger)

    # compute counts
    winner_votes = post["votes"].get(winner, 0)
    flag_count   = len(post["flags"])
    like_count   = len(post["likes"])
    net_flags    = max(0, flag_count - like_count)

    # compute ratio based on original votes
    flag_ratio = (net_flags / winner_votes) if winner_votes > 0 else 0

    # if net flags ≥ 40% of winner’s votes, interrupt and switch
    if flag_ratio >= 0.4:
        post["started"] = False
        second = post.get("second")

        if second:
            post["winner"] = second
            result = {
                "status": "Duel interrupted due to net flags on winner.",
                "switched_to": second
            }
            # schedule new timer for the next winner
            scheduler.add_job(
                handle_duel_timeout,
                'date',
                run_date=datetime.now() + timedelta(hours=2),
                args=[post_id]
            )
        else:
            result = {
                "status": "Duel interrupted but no second user available.",
                "switched_to": None
            }

        # reset flags and likes for the next round
        post["flags"] = []
        post["likes"] = []
        post["postponed"] = False
        save_data()
        return jsonify(result), 200

    save_data()
    return jsonify({
        "status": f"Flag registered on '{winner}'. Net flags: {net_flags}/{winner_votes}."
    }), 200



@app.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):
    """
    Register a ‘like’ for the current duel winner.
    Likes can offset flags 1:1.
    """
    data = request.json
    liker = data.get("user")
    post = posts.get(post_id)

    if not post:
        return jsonify({"error": "Post not found."}), 404

    winner = post.get("winner")
    if not winner:
        return jsonify({"error": "No winner to like."}), 400

    # init likes list if missing
    if "likes" not in post:
        post["likes"] = []

    if liker in post["likes"]:
        return jsonify({"error": f"User '{liker}' has already liked the winner."}), 403

    post["likes"].append(liker)
    save_data()
    return jsonify({
        "status": f"Like registered on '{winner}'. Total likes: {len(post['likes'])}"
    }), 200


@app.route("/status/<post_id>", methods=["GET"])
def get_status(post_id):
    """Return full post state including body, comments, votes, flags, winner, second."""
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    return jsonify({
        "body": post["body"],
        "winner": post["winner"],
        "second": post["second"],
        "postponed": post["postponed"],
        "started": post["started"],
        "votes": post["votes"],
        "voted_users": post["voted_users"],
        "flags": post["flags"],
        "comments": post["comments"],
        "commenters": post["commenters"]
    }), 200

@app.route("/results/<post_id>", methods=["GET"])
def get_results(post_id):
    """Return vote ranking, top two commenters, and post body for a post."""
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    ranking = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    return jsonify({
        "body": post["body"],
        "ranking": ranking,
        "winner": post.get("winner"),
        "second": post.get("second")
    }), 200

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
