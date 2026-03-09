"""Challenge service — timed kindness challenges."""
from datetime import datetime, timezone, timedelta

from app.extensions import db
from app.models.challenge import Challenge
from app.models.social import Friend
from app.services.ledger_service import deduct_points, add_gems
from app.utils.errors import NotFoundError, APIError




def send_challenge_to_friend(
    sender_id,
    recipient_email,
    description=None,
    cost_points=50,
    duration_minutes=60,
    reward_gems=5,
):
    """
    Send a timed challenge to a friend.
    • Costs the sender `cost_points` (default 50).
    • Creates an active challenge assigned to the recipient.
    • Recipient earns `reward_gems` (default 5) on verified completion.
    """
    from app.models.user import User
    from app.models.quest import Quest
    from sqlalchemy.sql.expression import func

    # Verify recipient exists by email (case-insensitive)
    recipient = User.query.filter(User.email.ilike(recipient_email)).first()
    if not recipient:
        raise NotFoundError('Friend with that email not found')
        
    recipient_id = recipient.id

    if sender_id == recipient_id:
        raise APIError('Cannot send a challenge to yourself', 400)

    # Verify they are friends (either direction)
    friendship = Friend.query.filter(
        (
            (Friend.user_id == sender_id) & (Friend.friend_user_id == recipient_id)
        ) | (
            (Friend.user_id == recipient_id) & (Friend.friend_user_id == sender_id)
        ),
        Friend.status == 'accepted',
    ).first()
    if not friendship:
        raise APIError('You can only send challenges to friends', 400)

    # Deduct points from sender
    deduct_points(sender_id, cost_points, 'challenge_sent')
    
    # Pick a random "hard" quest, or fallback if none exist
    final_description = description
    if not final_description:
        hard_quest = Quest.query.filter_by(difficulty_hint='hard', active=True).order_by(func.random()).first()
        if hard_quest:
            final_description = f"{hard_quest.title}: {hard_quest.description}"
        elif description:
             final_description = description
        else:
             final_description = 'A kindness challenge from your friend!'

    now = datetime.now(timezone.utc)
    challenge = Challenge(
        user_id=recipient_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        description=final_description,
        started_at=now,
        expires_at=now + timedelta(minutes=duration_minutes),
        status='active',
        cost_points=0,  # recipient pays nothing
        challenge_type='received',
    )
    db.session.add(challenge)
    db.session.flush()
    return challenge, reward_gems


def submit_challenge_proof(challenge_id, proof_id, user_id):
    """Submit proof for a challenge."""
    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        raise NotFoundError('Challenge not found')
    if challenge.user_id != user_id:
        raise APIError('Not your challenge', 403)
    if challenge.status != 'active':
        raise APIError(f'Challenge is not active (status: {challenge.status})', 400)

    # Check expiry
    now = datetime.now(timezone.utc)
    # Fix naive datetime comparison
    challenge_expires = challenge.expires_at
    if challenge_expires.tzinfo is None:
        challenge_expires = challenge_expires.replace(tzinfo=timezone.utc)
        
    if now > challenge_expires:
        challenge.status = 'expired'
        db.session.flush()
        raise APIError('Challenge has expired', 400)

    challenge.proof_id = proof_id
    challenge.status = 'pending_review'
    db.session.flush()
    return challenge


def complete_challenge(challenge_id, verified=True, reward_gems=5):
    """
    Complete or reject a challenge based on verification.
    Awards gems on success.
    """
    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        raise NotFoundError('Challenge not found')

    if verified:
        challenge.status = 'completed'
        if not challenge.reward_given:
            add_gems(challenge.user_id, reward_gems, 'challenge_completed', related_id=challenge.id)
            challenge.reward_given = True
    else:
        challenge.status = 'failed'

    db.session.flush()
    return challenge


def expire_stale_challenges():
    """Mark all expired active challenges as 'expired'. Call periodically."""
    now = datetime.now(timezone.utc)
    stale = Challenge.query.filter(
        Challenge.status == 'active',
        Challenge.expires_at < now,
    ).all()
    for c in stale:
        c.status = 'expired'
    db.session.commit()
    return len(stale)


