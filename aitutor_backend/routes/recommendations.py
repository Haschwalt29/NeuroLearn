from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.recommendation_engine import RecommendationEngine
from ..models import User

recommendations_bp = Blueprint("recommendations", __name__)
engine = RecommendationEngine()

@recommendations_bp.get("/recommendations/content")
@jwt_required()
def get_content_recommendations():
    user_id = int(get_jwt_identity())
    recommendations = engine.get_content_recommendations(user_id)
    return jsonify({"recommendations": recommendations})

@recommendations_bp.get("/recommendations/difficulty")
@jwt_required()
def get_adaptive_difficulty():
    user_id = int(get_jwt_identity())
    difficulty = engine.calculate_learning_difficulty(user_id)
    return jsonify({"difficulty": difficulty})

@recommendations_bp.get("/recommendations/message")
@jwt_required()
def get_adaptive_message():
    user_id = int(get_jwt_identity())
    message = engine.get_adaptive_message(user_id)
    return jsonify({"message": message})

@recommendations_bp.get("/recommendations/break")
@jwt_required()
def should_take_break():
    user_id = int(get_jwt_identity())
    should_break = engine.should_suggest_break(user_id)
    return jsonify({"should_break": should_break})

@recommendations_bp.get("/recommendations/insights")
@jwt_required()
def get_emotion_insights():
    user_id = int(get_jwt_identity())
    days = int(request.args.get('days', 7))
    insights = engine.get_emotion_insights(user_id, days)
    return jsonify(insights)

@recommendations_bp.get("/recommendations/trend")
@jwt_required()
def get_emotion_trend():
    user_id = int(get_jwt_identity())
    hours = int(request.args.get('hours', 24))
    trend = engine.get_emotion_trend(user_id, hours)
    return jsonify(trend)
