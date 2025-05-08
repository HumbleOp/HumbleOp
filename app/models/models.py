from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association Table for Self-Referential Follows
follows = db.Table(
    'follows',
    db.Column('follower', db.String, db.ForeignKey('users.username'), primary_key=True),
    db.Column('followed', db.String, db.ForeignKey('users.username'), primary_key=True)
)

class User(db.Model):
    """Model representing a user in the system."""
    __tablename__ = 'users'

    # Columns
    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String, nullable=False)
    token = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String, default='')
    bio = db.Column(db.String, default='')

    # Relationships
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='voter', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('Badge', backref='user', lazy=True, cascade='all, delete-orphan')

    following = db.relationship(
        'User',  # Self-referential relationship
        secondary=follows,
        primaryjoin=lambda: follows.c.follower == User.username,
        secondaryjoin=lambda: follows.c.followed == User.username,
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Post(db.Model):
    """Model representing a post."""
    __tablename__ = 'posts'

    # Columns
    id = db.Column(db.String, primary_key=True)
    author = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    started = db.Column(db.Boolean, default=False)
    postponed = db.Column(db.Boolean, default=False)
    winner = db.Column(db.String, db.ForeignKey('users.username'))
    second = db.Column(db.String, db.ForeignKey('users.username'))

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='post', lazy=True, cascade='all, delete-orphan')
    flags = db.relationship('Flag', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    """Model representing a comment on a post."""
    __tablename__ = 'comments'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    commenter = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    text = db.Column(db.Text, nullable=False)

class Vote(db.Model):
    """Model representing a vote on a post."""
    __tablename__ = 'votes'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    voter = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    candidate = db.Column(db.String, nullable=False)

class Flag(db.Model):
    """Model representing a flag on a post."""
    __tablename__ = 'flags'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    flagger = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

class Like(db.Model):
    """Model representing a like on a post."""
    __tablename__ = 'likes'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    liker = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

class Badge(db.Model):
    """Model representing a badge awarded to a user."""
    __tablename__ = 'badges'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    name = db.Column(db.String, nullable=False)
