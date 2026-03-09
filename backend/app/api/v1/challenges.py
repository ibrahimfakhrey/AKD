"""Challenges API — timed kindness challenges."""
import os
import uuid

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.challenge import Challenge
from app.models.proof import Proof
from app.services.challenge_service import (
    submit_challenge_proof, complete_challenge,
    send_challenge_to_friend,
)
from app.services.verification_service import get_verifier
from app.utils.errors import APIError, NotFoundError

challenges_bp = Blueprint('challenges', __name__, url_prefix='/api/v1/challenges')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@challenges_bp.route('/send', methods=['POST'])
@jwt_required()
def send():
    """Send a challenge to a friend. Costs 50 points; friend has 1 hour; earns 5 gems."""
    sender_id = get_jwt_identity()
    data = request.get_json() or {}

    recipient_email = data.get('friend_email')
    if not recipient_email:
        raise APIError('friend_email is required')

    cost = current_app.config.get('CHALLENGE_SEND_COST_POINTS', 50)
    duration = current_app.config.get('CHALLENGE_DURATION_MINUTES', 60)
    reward_gems = current_app.config.get('CHALLENGE_REWARD_GEMS', 5)

    challenge, _ = send_challenge_to_friend(
        sender_id=sender_id,
        recipient_email=recipient_email,
        description=data.get('description'),
        cost_points=cost,
        duration_minutes=duration,
        reward_gems=reward_gems,
    )
    db.session.commit()
    return jsonify(challenge.to_dict()), 201


@challenges_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active():
    user_id = get_jwt_identity()
    challenge = Challenge.query.filter_by(user_id=user_id, status='active').first()
    if not challenge:
        return jsonify(None)
    return jsonify(challenge.to_dict())


@challenges_bp.route('/received', methods=['GET'])
@jwt_required()
def get_received():
    """Get challenges sent to the current user by friends."""
    user_id = get_jwt_identity()
    challenges = (
        Challenge.query
        .filter_by(recipient_id=user_id, challenge_type='received')
        .filter(Challenge.status.in_(['active', 'pending_review']))
        .order_by(Challenge.started_at.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in challenges])


@challenges_bp.route('/<challenge_id>/submit', methods=['POST'])
@jwt_required()
def submit_proof(challenge_id):
    user_id = get_jwt_identity()

    if 'photo' not in request.files:
        raise APIError('No photo file provided')

    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename):
        raise APIError('Invalid file')

    # Save file
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # AI verify
    verifier = get_verifier(current_app.config.get('AI_VERIFIER_TYPE', 'mock'))
    result = verifier.verify(filepath)

    proof = Proof(
        user_id=user_id,
        file_url=f'/uploads/{filename}',
        ai_verification_result=result,
        verified=result.get('verified', False),
        verifier=result.get('verifier', 'ai'),
        verifier_confidence=result.get('confidence', 0.0),
    )
    db.session.add(proof)
    db.session.flush()

    challenge = submit_challenge_proof(challenge_id, proof.id, user_id)

    # Auto-complete if AI verified with high confidence
    reward_gems = current_app.config.get('CHALLENGE_REWARD_GEMS', 5)
    if proof.verified and proof.verifier_confidence >= 0.7:
        challenge = complete_challenge(challenge_id, verified=True, reward_gems=reward_gems)

    db.session.commit()
    return jsonify({
        'challenge': challenge.to_dict(),
        'proof': proof.to_dict(),
        'verification': result,
    })


@challenges_bp.route('/', methods=['GET'])
@jwt_required()
def list_challenges():
    user_id = get_jwt_identity()
    challenges = (
        Challenge.query
        .filter_by(user_id=user_id)
        .order_by(Challenge.started_at.desc())
        .limit(20)
        .all()
    )
    return jsonify([c.to_dict() for c in challenges])

