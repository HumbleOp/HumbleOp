[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Built with: Python & Flask](https://img.shields.io/badge/built%20with-Flask%20%7C%20Python-blue)](#)  
![Status: Private](https://img.shields.io/badge/repo-private-red)

**HumbleOp** is a meritocratic, API-driven debate platform where every voice counts, dialogue stays rich and concise, freedom of expression is protected, and mutual respect is non-negotiable.

- **Meritocracy First**  
  Every contribution is judged on its own merits: the best ideas rise to the top, regardless of who posts them.

- **Rich, Focused Conversations**  
  One comment per user, sharp voting mechanics, and timed 1-on-1 duels ensure every exchange is high-signal and outcome-oriented.

- **Freedom & Respect**  
  Uncensored dialogue within clear, community-enforced guidelines—flag abusive behavior to maintain a safe, respectful space.

---

## ✨ Core Features

- 🗳️ **Community Voting**: one vote per user, real-time tallies  
- 💬 **Single-Shot Comments**: concise, thoughtful contributions, one per user  
- 🏆 **Duel Mechanic**: top-voted respondent vs. original poster in a timed exchange  
- ⏱️ **Auto-Switch**: if the winner is inactive, the duel passes to the runner-up  
- 🚩 **Flag & Like**: crowd-moderation with net-flags logic (flags − likes ≥ 60%)  
- 🔒 **Secure Auth**: Argon2id password hashing, token-based login  
- 🤝 **Social Graph**: follow/unfollow, user profiles with badges

---

## 🚀 How to Run

1. **Clone the repo**  
   ```bash
   git clone https://github.com/HumbleOp/HumbleOp.git
   cd HumbleOp

2. Create a virtual enviroment:
   python -m venv venv
   .\venv\Scripts\activate   # On Windows

3. Install dependencies:
   pip install -r requirements.txt  # includes argon2-cffi

4. Run the app:
   python humblecore.py

🔒 Security
Auth uses Argon2id with parameters:

time_cost=2

memory_cost=51200 (KiB, cioè 50 MiB)

parallelism=8

📡 API Endpoints

Authentication & Profile
| Method | Endpoint    | Body                        | Description                      |
| ------ | ----------- | --------------------------- | -------------------------------- |
| POST   | `/register` | `{ "username","password" }` | Register a new user              |
| POST   | `/login`    | `{ "username","password" }` | Authenticate and receive a token |
| GET    | `/profile`  | *(none)*                    | Get own profile (Bearer token)   |
| PUT    | `/profile`  | `{ "avatar_url", "bio" }`   | Update avatar & bio              |

Social
| Method | Endpoint               | Description               |
| ------ | ---------------------- | ------------------------- |
| POST   | `/follow/<username>`   | Follow another user       |
| POST   | `/unfollow/<username>` | Unfollow another user     |
| GET    | `/following`           | List users you follow     |
| GET    | `/followers`           | List users who follow you |

Posts & Duels
| Method | Endpoint                 | Body                           | Description                                                                        |
| ------ | ------------------------ | ------------------------------ | ---------------------------------------------------------------------------------- |
| POST   | `/create_post/<post_id>` | `{ "body": "Your question…" }` | Create a new duel-type post                                                        |
| POST   | `/comment/<post_id>`     | `{ "text": "Your comment…" }`  | Add exactly one comment per post (login required)                                  |
| GET    | `/comments/<post_id>`    | *(none)*                       | List all comments with current vote counts                                         |
| POST   | `/vote/<post_id>`        | `{ "candidate": "username" }`  | Cast one vote for a comment (login required)                                       |
| POST   | `/start_duel/<post_id>`  | *(none)*                       | Lock in winner/second and start the 2 h duel timer                                 |
| POST   | `/start_now/<post_id>`   | *(none)*                       | Manually mark the duel as started by the winner                                    |
| GET    | `/results/<post_id>`     | *(none)*                       | Get comment ranking, current winner & second                                       |
| POST   | `/flag/<post_id>`        | *(none)*                       | Flag the active winner (net-flags ≥60% → switch)                                   |
| POST   | `/like/<post_id>`        | *(none)*                       | Like the active winner (offsets flags 1 : 1)                                       |
| GET    | `/status/<post_id>`      | *(none)*                       | Get full duel state (body, comments, votes, flags, likes, winner, second, timers…) |


Made with 💡 and Python. Private MVP for internal testing.

---

Feel free to tweak any thresholds or phrasing—let me know if you’d like further edits!
