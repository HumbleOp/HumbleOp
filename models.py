from core.extensions import db
from datetime import datetime, UTC

post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.String, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_name', db.String, db.ForeignKey('tags.name'), primary_key=True)
)


follows = db.Table(
    'follows',
    db.Column('follower', db.String, db.ForeignKey('users.username'), primary_key=True),
    db.Column('followed', db.String, db.ForeignKey('users.username'), primary_key=True),
)

class User(db.Model):
    __tablename__  = 'users'
    username       = db.Column(db.String, primary_key=True)
    email          = db.Column(db.String, unique=True, nullable=False)
    password_hash  = db.Column(db.String, nullable=False)
    token          = db.Column(db.String, unique=True)
    avatar_url     = db.Column(db.String, default='')
    bio            = db.Column(db.String, default='')
    email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String, nullable=True)

    comments = db.relationship('Comment', backref='author', lazy=True)
    votes    = db.relationship('Vote',    backref='voter_user', lazy=True)
    badges   = db.relationship('Badge',   backref='user_owner', lazy=True)
    following = db.relationship(
        'User', secondary=follows,
        primaryjoin=lambda: follows.c.follower == User.username,
        secondaryjoin=lambda: follows.c.followed == User.username,
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Post(db.Model):
    __tablename__ = 'posts'
    id        = db.Column(db.String, primary_key=True)
    author    = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    body      = db.Column(db.Text,   nullable=False)
    started   = db.Column(db.Boolean, default=False)
    postponed = db.Column(db.Boolean, default=False)
    winner    = db.Column(db.String, db.ForeignKey('users.username'))
    second    = db.Column(db.String, db.ForeignKey('users.username'))
    initial_votes = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    voting_deadline = db.Column(db.DateTime, nullable=True)
    duel_start_time = db.Column(db.DateTime, nullable=True)
    duel_completed_by_author = db.Column(db.Boolean, default=False)
    duel_completed_by_winner = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)

    comments = db.relationship('Comment', backref='posts', lazy=True)
    votes    = db.relationship('Vote',    backref='posts', lazy=True)
    flags    = db.relationship('Flag',    backref='posts', lazy=True)
    likes    = db.relationship('Like',    backref='posts', lazy=True)
    media_urls = db.Column(db.JSON, default=list)


class Comment(db.Model):
    __tablename__ = 'comments'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String,  db.ForeignKey('posts.id'), nullable=False)
    commenter = db.Column(db.String,  db.ForeignKey('users.username'), nullable=False)
    text      = db.Column(db.Text,    nullable=False)
    is_duel = db.Column(db.Boolean, default=False)
    votes_rel = db.relationship("Vote", backref="comment", lazy="dynamic", foreign_keys="Vote.comment_id")


class Vote(db.Model):
    __tablename__ = 'votes'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String,  db.ForeignKey('posts.id'), nullable=False)
    voter     = db.Column(db.String,  db.ForeignKey('users.username'), nullable=False)
    candidate = db.Column(db.String,  nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))


class Flag(db.Model):
    __tablename__ = 'flags'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String,  db.ForeignKey('posts.id'), nullable=False)
    flagger   = db.Column(db.String,  db.ForeignKey('users.username'), nullable=False)

class Like(db.Model):
    __tablename__ = 'likes'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String,  db.ForeignKey('posts.id'), nullable=False)
    liker     = db.Column(db.String,  db.ForeignKey('users.username'), nullable=False)

class Badge(db.Model):
    __tablename__ = 'badges'
    id   = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String,  db.ForeignKey('users.username'), nullable=False)
    name = db.Column(db.String,  nullable=False)

class Tag(db.Model):
    __tablename__ = 'tags'
    name = db.Column(db.String(30), primary_key=True)

    posts = db.relationship(
        'Post',
        secondary=post_tags,
        backref=db.backref('tags', lazy='dynamic'),
        lazy='dynamic'
    )
