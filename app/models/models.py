from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for self-referential follows
follows = db.Table(
    'follows',
    db.Column('follower', db.String, db.ForeignKey('users.username'), primary_key=True),
    db.Column('followed', db.String, db.ForeignKey('users.username'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String, nullable=False)
    token = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String, default='')
    bio = db.Column(db.String, default='')

    # Relationships
    comments = db.relationship('Comment', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='voter', lazy=True)
    badges = db.relationship('Badge', backref='user', lazy=True)

    following = db.relationship(
        'User',
        secondary=follows,
        primaryjoin=lambda: follows.c.follower == User.username,
        secondaryjoin=lambda: follows.c.followed == User.username,
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.String, primary_key=True)
    author = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    started = db.Column(db.Boolean, default=False)
    postponed = db.Column(db.Boolean, default=False)
    winner = db.Column(db.String, db.ForeignKey('users.username'))
    second = db.Column(db.String, db.ForeignKey('users.username'))
    comments = db.relationship('Comment', backref='post', lazy=True)
    votes = db.relationship('Vote', backref='post', lazy=True)
    flags = db.relationship('Flag', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    commenter = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    text = db.Column(db.Text, nullable=False)

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    voter = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    candidate = db.Column(db.String, nullable=False)

class Flag(db.Model):
    __tablename__ = 'flags'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    flagger = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    liker = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    name = db.Column(db.String, nullable=False)