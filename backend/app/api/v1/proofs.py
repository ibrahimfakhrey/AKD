"""Proofs API — view proof details."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.proof import Proof
from app.utils.errors import NotFoundError, APIError

proofs_bp = Blueprint('proofs', __name__, url_prefix='/api/v1/proofs')


@proofs_bp.route('/<proof_id>', methods=['GET'])
@jwt_required()
def get_proof(proof_id):
    user_id = get_jwt_identity()
    proof = Proof.query.get(proof_id)
    if not proof:
        raise NotFoundError('Proof not found')
    # Only allow owner or admin to view
    if proof.user_id != user_id:
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            raise APIError('Access denied', 403)
    return jsonify(proof.to_dict())


@proofs_bp.route('/mine', methods=['GET'])
@jwt_required()
def my_proofs():
    user_id = get_jwt_identity()
    proofs = Proof.query.filter_by(user_id=user_id).order_by(Proof.upload_time.desc()).limit(50).all()
    return jsonify([p.to_dict() for p in proofs])
