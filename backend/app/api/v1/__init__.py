"""API v1 package — registers all blueprints."""
from app.api.v1.auth import auth_bp
from app.api.v1.quests import quests_bp
from app.api.v1.proofs import proofs_bp
from app.api.v1.challenges import challenges_bp
from app.api.v1.friends import friends_bp
from app.api.v1.shop import shop_bp
from app.api.v1.leaderboard import leaderboard_bp
from app.api.v1.admin import admin_bp

all_blueprints = [
    auth_bp,
    quests_bp,
    proofs_bp,
    challenges_bp,
    friends_bp,
    shop_bp,
    leaderboard_bp,
    admin_bp,
]
