Week 1 – Backend core

[x] Flag & winner switch (net‐flags ≥ 60% → switch to second)

[x] Initial 2 h duel timer + 6 h postponement

[x] One comment per user under each post

[x] Vote on comments, recalc winner/second

[x] Persistence in data.json (temporary, poi spostato su SQLite)

[x] Separation of create_post vs start_duel

[x] GET /results/<post_id> endpoint

[ ] Internal event logging (votes, flags, switches)


Week 2 – Duel balancing & enhancements

[x] /like endpoint to offset flags 1:1

[x] Net‐flags logic in /flag (flags − likes ≥ 60% of winner’s votes)

[x] Automatic timer for the new winner after a switch

[ ] Codelogging of duel events (console or file)


Week 3 – Core social features

[ ] Post body enhancements (Markdown support, images/videos)

[x] Persistent user accounts & profiles in SQLite

Stored via SQLAlchemy

Fields: username, avatar URL, bio, badges, following, followers



Week 4 – Authentication

[x] User registration (POST /register)

[x] User login (POST /login) with Argon2id

[x] Auth middleware to protect comment/vote/flag/like endpoints


Week 5 – Frontend MVP

[ ] Simple UI for:

Registration & login

Creating a post (title, body, media)

Commenting, voting, liking & flagging

Starting duel & live timer display

Viewing comments, ranking & results



Week 6 – User profiles & badges

[ ] Profile page for each user:

Avatar (upload or URL)

Biography field

Earned badges

List of created posts & comments



Week 7 – Refining & Deploy

[ ] Bug fixes & edge‐case handling

[x] Migrate persistence JSON → SQLite (SQLAlchemy)

[ ] Public deploy (Render, Railway, ecc.)

[ ] Beta testing con utenti reali


Week 8 – ORM cleanup & Tests

[x] Database models: Users, Posts, Comments, Votes, Flags, Likes, Badges

[x] Self‐follow association table

[x] DB initialization helper (setup_db.py)

[x] test_database.py per verifica schema

[ ] Pytest suite per endpoint (auth, CRUD, duel logic)

<!-- bump for push -->