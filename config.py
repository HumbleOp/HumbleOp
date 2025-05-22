# config.py
# Central configuration file for HumbleOp application constants

# ——————————————————————————————————————————————————
# Duel thresholds
MIN_INITIAL_VOTES     = 50    # minimum initial like capital
MAX_INITIAL_VOTES     = 500   # maximum initial like capital
FLAG_RATIO_THRESHOLD  = 0.60  # flag percentage threshold to trigger switch
MIN_FLAGS_RATIO       = 0.05  # minimum flag count ratio relative to initial_votes to consider switch
NET_SCORE_RATIO       = 0.40  # net-score threshold (40% of initial_votes)

# ——————————————————————————————————————————————————
# Badge thresholds
INSIGHTFUL_THRESHOLD         = 20   # likes required for 'Insightful Speaker' badge
SERIAL_VOTER_THRESHOLD       = 10   # votes required for 'Serial Voter' badge
CONSISTENT_DEBATER_THRESHOLD = 10   # duels won for 'Consistent Debater' badge

# ——————————————————————————————————————————————————
# Scheduler delays (in hours)
DUEL_TIMEOUT_INITIAL_HOURS   = 2    # hours before duel timeout
DUEL_TIMEOUT_POSTPONE_HOURS  = 6    # hours to postpone duel after first timeout
DUEL_TIMEOUT_RETRY_HOURS     = 2    # hours before retrying duel after postpone

# ——————————————————————————————————————————————————
# Email settings
DEBUG_EMAIL                  = True  # enable fake email printing for development/testing
