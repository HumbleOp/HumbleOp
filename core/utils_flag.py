# Utility module to evaluate flags on a duel post and switch winner if thresholds are met

from datetime import datetime, timedelta
from sqlalchemy import func
from core.extensions import db, scheduler
from models import Like, Flag
from core.utils import handle_duel_timeout
from config import (
    MIN_FLAGS_RATIO,
    FLAG_RATIO_THRESHOLD,
    NET_SCORE_RATIO,
    DUEL_TIMEOUT_INITIAL_HOURS
)


def evaluate_flags_and_maybe_switch(post):
    """
    Check flags vs likes (with initial_votes offset) and decide whether to interrupt the duel.
    Returns (switched: bool, old_winner: str|None, new_winner: str|None).
    """
    # 1) Base counts
    initial_votes = post.initial_votes or 0
    actual_likes = db.session.query(func.count(Like.id)).filter_by(post_id=post.id).scalar() or 0
    total_flags = db.session.query(func.count(Flag.id)).filter_by(post_id=post.id).scalar() or 0

    # 2) Minimum flags required
    min_flags = max(int(initial_votes * MIN_FLAGS_RATIO), 5)

    # 3) Compute ratios and net score
    total_interactions = initial_votes + actual_likes + total_flags
    flag_ratio = (total_flags / total_interactions) if total_interactions > 0 else 0
    net_score = (initial_votes + actual_likes) - total_flags
    threshold_score = initial_votes * NET_SCORE_RATIO

    print(f"[SWITCH?] flags={total_flags}, min={min_flags}, ratio={flag_ratio:.2f}, net={net_score}, threshold={threshold_score}")
    print(f"[SWITCH?] current winner: {post.winner}, second: {post.second}")

    # 4) Decide switch
    if post.second and total_flags >= min_flags and (
        flag_ratio > FLAG_RATIO_THRESHOLD or
        net_score <= threshold_score
    ):
        old_winner = post.winner
        new_winner = post.second

        post.started = False
        post.postponed = False
        post.winner = new_winner

        db.session.query(Flag).filter_by(post_id=post.id).delete()
        db.session.query(Like).filter_by(post_id=post.id).delete()

        scheduler.add_job(
            handle_duel_timeout,
            'date',
            run_date=datetime.now() + timedelta(hours=DUEL_TIMEOUT_INITIAL_HOURS),
            args=[post.id]
        )
        db.session.commit()

        print(f"[SWITCH] WINNER CHANGED from {old_winner} to {new_winner}")
        return True, old_winner, new_winner

    return False, None, None
