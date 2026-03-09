"""Quest service — daily quest generation and completion logic."""
from datetime import date

from sqlalchemy.sql.expression import func

from app.extensions import db
from app.models.quest import Quest, DailyQuest
from app.utils.errors import NotFoundError, APIError


def get_or_generate_daily_quests(user_id, quest_count=3):
    """
    Return today's daily quests for a user.
    If they don't have any yet, pick random active quests and assign them.
    """
    today = date.today()
    existing = DailyQuest.query.filter_by(user_id=user_id, date=today).all()

    if existing:
        return existing

    # Pick random active quests
    available = Quest.query.filter(Quest.active == True, Quest.difficulty_hint != 'hard').order_by(func.random()).limit(quest_count).all()

    if not available:
        raise APIError('No active quests available. Ask an admin to create some.', 503)

    daily_quests = []
    for quest in available:
        dq = DailyQuest(
            user_id=user_id,
            quest_id=quest.id,
            date=today,
            status='assigned',
        )
        db.session.add(dq)
        daily_quests.append(dq)

    db.session.flush()
    return daily_quests


def submit_quest_proof(daily_quest_id, proof_id, user_id):
    """Attach a proof to a daily quest and mark as pending review."""
    dq = DailyQuest.query.get(daily_quest_id)
    if not dq:
        raise NotFoundError('Daily quest not found')
    if dq.user_id != user_id:
        raise APIError('Not your quest', 403)
    if dq.status not in ('assigned',):
        raise APIError(f'Quest cannot be submitted (status: {dq.status})', 400)

    dq.proof_id = proof_id
    dq.status = 'pending_review'
    db.session.flush()
    return dq


def complete_quest(daily_quest_id, verified=True):
    """
    Mark a quest as completed or rejected based on verification result.
    Called after AI or manual review.
    """
    from app.services.ledger_service import add_points

    dq = DailyQuest.query.get(daily_quest_id)
    if not dq:
        raise NotFoundError('Daily quest not found')

    if verified:
        dq.status = 'completed'
        if not dq.reward_awarded:
            quest = Quest.query.get(dq.quest_id)
            add_points(dq.user_id, quest.reward_points, 'quest_completed', related_id=dq.id)
            dq.reward_awarded = True
    else:
        dq.status = 'rejected'

    db.session.flush()
    return dq
