# HumbleOp

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Built with: Python & Flask](https://img.shields.io/badge/built%20with-Flask%20%7C%20Python-blue)](#)
![Status: Private](https://img.shields.io/badge/repo-private-red)

**HumbleOp** is a minimal social discussion platform where opinions are challenged fairly, transparently, and intelligently.  
The community votes on responses, and the most voted user earns the right to debate the original author — 1-on-1.

---

## ✨ Core Features

- 🗳️ **Voting system** to select the top responses  
- 🏆 **Duel mechanic** between post author and top-voted responder  
- ⏱️ **Timers** and auto-switch if the winner is inactive  
- 🚩 (Coming soon) **Flag system** to moderate toxic conversations  
- 📦 API-based architecture, built in Flask (no frontend yet)

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/HumbleOp/HumbleOp.git
   cd HumbleOp


Create a virtual environment:
python -m venv venv
.\venv\Scripts\activate   # On Windows


Install dependencies:
pip install -r requirements.txt


Run the app:
python HumbleCore.py


📡 API Endpoints

| Method | Endpoint                | Description                              |
|--------|-------------------------|------------------------------------------|
| POST   | `/start_duel/<post_id>` | Start a duel for a post                  |
| POST   | `/start_now/<post_id>`  | Mark the duel as started by the winner   |
| GET    | `/status/<post_id>`     | Check current state of a post            |
| POST   | `/vote/<post_id>`       | Vote for a candidate on a post           |
| GET    | `/results/<post_id>`    | See ranking and vote count for a post    |

📜 License
This project is licensed under the MIT License.


Made with 💡 and Python. Private MVP for internal testing.


---

## 🛣️ Roadmap

- [x] Set up Flask backend
- [x] Implement duel timer with fallback to second-ranked user
- [x] Add voting system with one-vote-per-user logic
- [x] Auto-assign winner and second based on votes
- [x] Clean repository and remove old commits
- [x] Write full project README with badges
- [ ] Add flag system to moderate or interrupt duels
- [ ] Add persistent data storage (JSON or SQLite)
- [ ] Implement user identity (basic token or session)
- [ ] RESTful login/signup with authentication
- [ ] Create frontend prototype (React or Vite)
- [ ] Deploy demo online (Render, Vercel, Railway, etc.)

> ✅ This list evolves with the project. Feature status is updated with each commit.
