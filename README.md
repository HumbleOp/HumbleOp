# 🌐 HumbleOp

**HumbleOp** is a social debate platform where every opinion matters — but only once.  
Users share an opinion, others respond with a single reply, and the top-voted reply earns the right to duel with the author. One conversation. One chance. One winner.

---

## 🧠 Concept

- 🗣️ A user posts a single opinion (e.g. "Universities should be free.")
- 💬 Others reply — but can submit **only one** response per post.
- 🗳️ The community votes on the best reply.
- ⚔️ The top-voted responder enters a timed **1-on-1 debate** with the post author.
- 🚩 If the discussion becomes toxic, red flags can be raised (40% threshold).
- 🔁 If the top user is flagged out or inactive, the next-highest voted user takes their place.

---

## 🧪 MVP Features (Current)

- 🔹 Flask + APScheduler backend
- 🔹 In-memory post & duel management
- 🔹 Duel timeout with 1 optional postponement
- 🔹 Automatic switch to second-best reply
- 🔹 API endpoints for posting, starting, and checking status

---

## 🚀 How to Run (Locally)

1. Clone the repository:
   ```bash
   git clone https://github.com/HumbleOp/HumbleOp.git
   cd HumbleOp


(Recommended) Create a virtual environment:
python -m venv venv
.\venv\Scripts\activate   # Windows

Install dependencies:
pip install -r requirements.txt


Run the server:
python HumbleCore.py


Optional: Run the demo test script
python test_humbleop.py



API Endpoints
Method	URL	Description
POST	/start_duel/<post_id>	Creates a new opinion & assigns duel
POST	/start_now/<post_id>	Simulates user starting the duel
GET	/status/<post_id>	Returns current duel state



Contact
Created by @HumbleOp
Got feedback or want to collaborate? Open an issue or email us at fra.cossu.chem@gmail.com
