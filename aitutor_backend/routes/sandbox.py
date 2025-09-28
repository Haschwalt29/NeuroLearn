from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import CodingAttempt, User
from ..services.sandbox_service import run_code

sandbox_bp = Blueprint('sandbox', __name__)

@sandbox_bp.route('/run', methods=['POST'])
@jwt_required()
def run():
    payload = request.get_json(force=True) or {}
    language = (payload.get('language') or '').strip().lower()
    code = payload.get('code') or ''
    if not language or not code:
        return jsonify({ 'error': 'language and code are required' }), 400

    user_id = get_jwt_identity()
    result = run_code(language, code)

    attempt = CodingAttempt(
        user_id=user_id,
        language=language,
        code=code,
        output=result.output,
        error=result.error,
        status=result.status,
        exec_ms=result.exec_ms,
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({
        'output': result.output,
        'error': result.error,
        'status': result.status,
        'exec_ms': result.exec_ms,
    })


