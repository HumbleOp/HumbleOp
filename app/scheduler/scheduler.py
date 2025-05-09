<<<<<<< HEAD
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.utils.data_utils import save_data

scheduler = BackgroundScheduler()

def handle_duel_timeout(post_id, posts):
    post = posts.get(post_id)
    if not post or post.get("started"):
        return

    if not post.get("postponed"):
        post["postponed"] = True
        scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=6), args=[post_id, posts])
    else:
        post["winner"] = post.get("second")
        post["postponed"] = False
        post["started"] = False
        scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=2), args=[post_id, posts])

=======
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.utils.data_utils import save_data

scheduler = BackgroundScheduler()

def handle_duel_timeout(post_id, posts):
    post = posts.get(post_id)
    if not post or post.get("started"):
        return

    if not post.get("postponed"):
        post["postponed"] = True
        scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=6), args=[post_id, posts])
    else:
        post["winner"] = post.get("second")
        post["postponed"] = False
        post["started"] = False
        scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=2), args=[post_id, posts])

>>>>>>> bfa9cd8 (update)
    save_data(posts, "data.json")