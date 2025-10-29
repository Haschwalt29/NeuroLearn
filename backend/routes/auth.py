from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .. import db
from ..models import User
from ..services.colearner_service import get_or_create_profile

auth_bp = Blueprint("auth", __name__)

# Add CORS headers to all responses
@auth_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Handle preflight OPTIONS requests
@auth_bp.route("/<path:path>", methods=["OPTIONS"])
def handle_options(path):
    return "", 200


# Login and signup routes removed - no authentication required

@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": user.id, "email": user.email, "name": user.name, "role": user.role, "emotion_opt_in": user.emotion_opt_in})


@auth_bp.get("/health")
def health_check():
    """Health check endpoint for Render deployment"""
    return jsonify({"status": "healthy", "service": "neurolearn-backend"})


