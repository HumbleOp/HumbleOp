# HumbleOp

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Built with: Python & Flask](https://img.shields.io/badge/built%20with-Flask%20%7C%20Python-blue)](#)  
![Status: Private](https://img.shields.io/badge/repo-private-red)

**HumbleOp** is an API-driven discussion platform that turns open-ended questions into structured, outcome-oriented debates.  

1. **Post & Comment**  
   - Any user can create a “duel” by posting a statement or question.  
   - Each community member may submit exactly one comment per post, ensuring concise, thoughtful contributions.  

2. **Community Voting**  
   - Fellow users cast a single vote on the comment they find strongest.  
   - Votes are tallied in real time; the top-voted commentator becomes the “winner,” and the runner-up is the “second.”

3. **Timed 1-on-1 Duels**  
   - The original poster and the winning commentator enter a timed one-on-one exchange.  
   - If the winner fails to respond within the allotted window, the duel automatically passes to the second-place commentator.  

4. **Crowd-Driven Moderation**  
   - A lightweight flag system lets the community interrupt toxic duels.  
   - At 40% flags (relative to voters), the duel is halted and reassigned, maintaining a respectful environment.

Built with a minimal interface in mind, HumbleOp emphasizes clarity, brevity, and fair engagement—ideal for anyone who values structured, high-signal discussions over endless comment threads.


---

## ✨ Core Features

- 🗳️ **Voting system** to select the top responses  
- 🏆 **Duel mechanic** between post author and top-voted responder  
- ⏱️ **Timers** and auto-switch if the winner is inactive  
- 🚩 **Flag system** to moderate toxic conversations  
- 💬 **Comments**: one per user, voted by the community  
- 📦 API-based architecture, built in Flask (no frontend yet)

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/HumbleOp/HumbleOp.git
   cd HumbleOp

2. Create a virtual enviroment:
   python -m venv venv
   .\venv\Scripts\activate   # On Windows

3. Install dependencies:
   pip install -r requirements.txt

4. Run the app:
   python humblecore.py

📡 API Endpoints

| Method | Endpoint                 | Description                                                                                     |
| ------ | ------------------------ | ----------------------------------------------------------------------------------------------- |
| POST   | `/create_post/<post_id>` | Create a post: JSON `{ "author": "jack", "body": "Your text here" }`                            |
| POST   | `/comment/<post_id>`     | Add a comment (one per user): `{ "commenter":"alice","text":"..." }`                            |
| GET    | `/comments/<post_id>`    | List all comments with their current vote counts                                                |
| POST   | `/vote/<post_id>`        | Vote a comment (one vote per user): `{ "voter":"user1","candidate":"alice" }`                   |
| POST   | `/start_duel/<post_id>`  | Lock in winner/second and start the 2 h duel timer                                              |
| POST   | `/start_now/<post_id>`   | Manually mark the duel as started by the winner                                                 |
| GET    | `/results/<post_id>`     | Get comment ranking and display `winner` & `second`                                             |
| POST   | `/flag/<post_id>`        | Flag the active winner: net flags ≥ 40% of that winner’s votes → switch to second               |
| POST   | `/like/<post_id>`        | Like the active winner (offsets flags 1:1)                                                      |
| GET    | `/status/<post_id>`      | Get full post state (body, author, comments, votes, flags, likes, winner, second, timers, etc.) |


Made with 💡 and Python. Private MVP for internal testing.