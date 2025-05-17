# HumbleOp – Enter the Arena of Ideas
![Tests](https://github.com/HumbleOp/HumbleOp/actions/workflows/tests.yml/badge.svg)

**Not just a platform. A battleground for brains.**

HumbleOp is a high-signal, gamified debate arena where clarity triumphs over noise. Here, arguments collide in structured duels, badges are earned by skill, and reputation is built through consistency—not virality.

---

## What makes HumbleOp different?

### ⚔️ Duel-centric discussion
Every post launches a **1v1 intellectual duel**. One comment per user. No spam, no thread hijacking. The top-voted responder faces off against the original poster in a timed, transparent showdown. If they flake, the runner-up steps in. You win by clarity, logic, and presence.

### 🏆 Gamified progression
Earn badges for real accomplishments—not dopamine hits. From “First Blood” to “The Great Debater,” every title reflects action and merit. Consistency, eloquence, insight, and resilience are rewarded. There’s no leaderboard—only legacy.

### 🗳️ One shot, one vote
Each user gets a single vote per debate. No like-farming. Rankings are visible, votes are meaningful, and each one has consequences.

### 🚨 Community-powered moderation
Users can **flag** or **like** the winning debater. If too many flags overwhelm the support, the winner is auto-replaced. No moderators, no bias—just logic and math.

### 🔐 Radical transparency and security
Built on Flask with Argon2 password hashing. No data harvesting, no tracking, no algorithms dictating your experience. You own your identity and voice.

---

## Who is this for?

- **Thinkers** tired of shallow threads and outrage bait.
- **Writers** who want feedback that’s earned, not handed out.
- **Communities** that crave structured disagreement and respect.
- **Competitors** who thrive when the stakes are real.

If you want safe debates, stay on social media. If you're ready to *earn* your voice—welcome to the arena.

---

## Run it locally (MVP)

```bash
git clone https://github.com/your-username/humbleop-modular.git
cd humbleop-modular
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 and start dueling.

---

## Built With

- Python + Flask
- SQLite + SQLAlchemy
- Argon2id (password hashing)
- RESTful API-first architecture

---

## Feature Highlights

- ✅ One-shot comments, single-vote debates
- ✅ Timed 1v1 duels with auto-fallback
- ✅ Badge system for real merit
- ✅ User profiles, avatars, follower system
- ✅ Flag/like logic to self-moderate
- 🚧 Tagging, categories, and activity feeds (coming)
- 🚧 Public duel archive
- 🚧 Stripe-powered Pro tiers (future)

---

Made with clarity, not clout.
