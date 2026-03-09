"""Quests API — daily quests and proof submission."""
import os
import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.proof import Proof
from app.services.quest_service import get_or_generate_daily_quests, submit_quest_proof, complete_quest
from app.services.verification_service import get_verifier
from app.utils.errors import APIError

quests_bp = Blueprint('quests', __name__, url_prefix='/api/v1/quests')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@quests_bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_quests():
    user_id = get_jwt_identity()
    quest_count = current_app.config.get('DAILY_QUEST_COUNT', 3)
    daily_quests = get_or_generate_daily_quests(user_id, quest_count)
    db.session.commit()
    return jsonify([dq.to_dict() for dq in daily_quests])


@quests_bp.route('/<quest_id>/submit', methods=['POST'])
@jwt_required()
def submit_proof(quest_id):
    """Upload photo proof for a daily quest."""
    user_id = get_jwt_identity()

    if 'photo' not in request.files:
        raise APIError('No photo file provided')

    file = request.files['photo']
    if file.filename == '':
        raise APIError('No file selected')
    if not allowed_file(file.filename):
        raise APIError(f'Allowed file types: {", ".join(ALLOWED_EXTENSIONS)}')

    # Save file
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    file_url = f'/uploads/{filename}'

    # Run AI verification
    verifier = get_verifier(current_app.config.get('AI_VERIFIER_TYPE', 'mock'))
    result = verifier.verify(filepath)

    # Create proof record
    proof = Proof(
        user_id=user_id,
        file_url=file_url,
        ai_verification_result=result,
        verified=result.get('verified', False),
        verifier=result.get('verifier', 'ai'),
        verifier_confidence=result.get('confidence', 0.0),
    )
    db.session.add(proof)
    db.session.flush()

    # Attach proof to quest
    dq = submit_quest_proof(quest_id, proof.id, user_id)

    # If AI verified, auto-complete
    if proof.verified and proof.verifier_confidence >= 0.7:
        dq = complete_quest(quest_id, verified=True)

    db.session.commit()
    return jsonify({
        'daily_quest': dq.to_dict(),
        'proof': proof.to_dict(),
        'verification': result,
    })
