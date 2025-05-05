# Roadmap

### Week 1 – Backend core
- [x] Flag & winner switch (40% flags → switch to second)  
- [x] Initial 2 h duel timer + 6 h postponement  
- [x] Comment per user under each post  
- [x] Vote on comments, recalc winner/second  
- [x] Persistence in `data.json`  
- [x] Separation of **create_post** vs **start_duel**  
- [ ] `GET /results/<post_id>` endpoint  
- [ ] Internal event logging (votes, flags, switches)

### Week 2 – Duel balancing & enhancements
- [ ] **/like** endpoint to offset flags 1 : 1  
- [ ] Net-flags logic in `/flag` (flags − likes ≥ 40% of winner’s votes)  
- [ ] Automatic timer for the new winner after a switch  
- [ ] Codelogging of duel events (console or file)

### Week 3 – Core social features
- [ ] Post body enhancements (Markdown support, images/videos)  
- [ ] Persistent user accounts & profiles  
  - Store in `users.json` or SQLite  
  - Fields: username, avatar URL, bio, badges  

### Week 4 – Authentication
- [ ] User registration (`POST /register`)  
- [ ] User login (`POST /login`)  
- [ ] Auth middleware (protect comment/vote/flag/like)

### Week 5 – Frontend MVP
- [ ] Simple UI for:
  - Registration & login  
  - Creating a post (title, body, media)  
  - Commenting, voting, liking & flagging  
  - Start duel & live timer display  
  - Viewing comments, ranking & results

### Week 6 – User profiles & badges
- [ ] **Profile page** for each user:
  - Avatar (upload or URL)  
  - Biography field  
  - Earned badges (“Top Voter”, “First Comment”, etc.)  
  - List of created posts & comments

### Week 7 – Refining & Deploy
- [ ] Bug fixes & edge-case handling  
- [ ] Migrate persistence JSON → SQLite or other DB  
- [ ] Public deploy (Render, Railway, ecc.)  
- [ ] Beta testing with real users
