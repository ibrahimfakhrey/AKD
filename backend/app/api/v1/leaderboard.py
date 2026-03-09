"""Leaderboard API — points and gems rankings."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.leaderboard_service import get_points_leaderboard, get_gems_leaderboard

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/v1/leaderboard')


@leaderboard_bp.route('/points', methods=['GET'])
@jwt_required()
def points_leaderboard():
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    data = get_points_leaderboard(limit=limit, offset=offset)
    return jsonify(data)


@leaderboard_bp.route('/gems', methods=['GET'])
@jwt_required()
def gems_leaderboard():
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    data = get_gems_leaderboard(limit=limit, offset=offset)
    return jsonify(data)
