from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta
from flask import Flask
from app.models.models import db, Post

def check_postponed_duels():
    """Auto-start duels that have been postponed more than 30m."""
    # we assume this is always called *inside* an application context
    now = datetime.utcnow()
    for post in Post.query.filter_by(postponed=True):
        if post.updated_at + timedelta(minutes=30) <= now:
            post.postponed = False
            post.started   = True
    db.session.commit()

def init_scheduler(app: Flask):
    jobstores = {
        'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
    }
    sched = BackgroundScheduler(jobstores=jobstores)
    # schedule your job
    sched.add_job(check_postponed_duels, 'interval', minutes=1)
    sched.start()
    return sched
