"""Leaderboard service — rankings cached in memory (Redis-ready)."""
from app.models.user import User


def get_points_leaderboard(limit=50, offset=0):
    """Get top users by points."""
    users = (
        User.query
        .filter_by(is_banned=False)
        .order_by(User.points.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            'rank': offset + i + 1,
            'user_id': u.id,
            'display_name': u.display_name,
            'avatar_url': u.avatar_url,
            'points': u.points,
        }
        for i, u in enumerate(users)
    ]


def get_gems_leaderboard(limit=50, offset=0):
    """Get top users by gems."""
    users = (
        User.query
        .filter_by(is_banned=False)
        .order_by(User.gems.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            'rank': offset + i + 1,
            'user_id': u.id,
            'display_name': u.display_name,
            'avatar_url': u.avatar_url,
            'gems': u.gems,
        }
        for i, u in enumerate(users)
    ]
