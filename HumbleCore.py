from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from collections import defaultdict


app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# In-memory "database" of posts and duels
posts = {}  # post_id: {"winner": str, "second": str, "postponed": bool, "started": bool}


# ⏳ Called when the winner does not start the duel in time
def handle_duel_timeout(post_id):
    post = posts.get(post_id)
    if not post:
        print(f"[ERROR] Post {post_id} not found.")
        return

    if post.get("started"):
        print(f"[OK] Duel for {post_id} already started.")
        return

    if not post.get("postponed"):
        # First timeout → allow one postponement
        post["postponed"] = True
        print(f"[POSTPONED] First extension granted to {post['winner']}. 6 extra hours.")
        scheduler.add_job(
            handle_duel_timeout,
            trigger='date',
            run_date=datetime.now() + timedelta(hours=6),
            args=[post_id]
        )
    else:
        # Second timeout → switch to second-ranked user
        print(f"[SWITCH] {post['winner']} did not respond. Switching to {post['second']}.")
        post["winner"] = post["second"]
        post["postponed"] = False
        post["started"] = False
        print(f"[NOTIFICATION] {post['winner']} now has 2 hours to start the duel.")
        scheduler.add_job(
            handle_duel_timeout,
            trigger='date',
            run_date=datetime.now() + timedelta(hours=2),
            args=[post_id]
        )


# 🚀 Trigger the duel assignment (POST: /start_duel/<post_id>)
@app.route("/start_duel/<post_id>", methods=["POST"])
def start_duel(post_id):
    data = request.json
    winner = data.get("winner")
    second = data.get("second")

    if not winner or not second:
        return jsonify({"error": "Both 'winner' and 'second' are required."}), 400

    posts[post_id] = {
        "winner": winner,
        "second": second,
        "postponed": False,
        "started": False
    }

    print(f"[NOTIFICATION] {winner}, you have won! You have 2 hours to start the duel.")
    scheduler.add_job(
        handle_duel_timeout,
        trigger='date',
        run_date=datetime.now() + timedelta(hours=2),
        args=[post_id]
    )

    return jsonify({"status": "Duel timer started (2 hours)."}), 200


# ✅ Called when the winner actually starts the duel
@app.route("/start_now/<post_id>", methods=["POST"])
def user_started(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    post["started"] = True
    print(f"[STARTED] {post['winner']} has started the duel.")
    return jsonify({"status": "Duel successfully started."}), 200


# 🔍 Check the current state of a post (GET: /status/<post_id>)
@app.route("/status/<post_id>")
def get_status(post_id):
    return jsonify(posts.get(post_id, {"error": "Post not found."}))


# Initialize voting data for a post (if not present)
def init_post_votes(post_id):
    if "votes" not in posts[post_id]:
        posts[post_id]["votes"] = defaultdict(int)
        posts[post_id]["voted_users"] = set()


# 🗳️ Endpoint: cast a vote
@app.route("/vote/<post_id>", methods=["POST"])
def vote(post_id):
    data = request.json
    voter = data.get("voter")         # the user casting the vote
    candidate = data.get("candidate") # the user being voted for

    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    init_post_votes(post_id)

    if voter in post["voted_users"]:
        return jsonify({"error": f"User '{voter}' has already voted"}), 403

    post["votes"][candidate] += 1
    post["voted_users"].add(voter)

    # 🧠 Automatically update winner and second place
    sorted_votes = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    post["winner"] = sorted_votes[0][0] if len(sorted_votes) >= 1 else None
    post["second"] = sorted_votes[1][0] if len(sorted_votes) >= 2 else None

    return jsonify({
        "message": f"{voter} voted for {candidate}",
        "votes": post["votes"]
    }), 200


# 📊 Endpoint: get vote results
@app.route("/results/<post_id>", methods=["GET"])
def get_results(post_id):
    post = posts.get(post_id)
    if not post or "votes" not in post:
        return jsonify({"error": "No votes found for this post"}), 404

    sorted_votes = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    return jsonify({
        "ranking": sorted_votes,
        "winner": post.get("winner"),
        "second": post.get("second")
    }), 200



if __name__ == "__main__":
    app.run(debug=True)