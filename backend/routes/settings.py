from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import User

settings_bp = Blueprint("settings", __name__)


@settings_bp.get("/")
@jwt_required()
def get_settings():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"emotion_opt_in": user.emotion_opt_in})


@settings_bp.post("/")
@jwt_required()
def update_settings():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "not found"}), 404
    data = request.get_json() or {}
    if "emotion_opt_in" in data:
        user.emotion_opt_in = bool(data["emotion_opt_in"])
    db.session.commit()
    return jsonify({"emotion_opt_in": user.emotion_opt_in})


