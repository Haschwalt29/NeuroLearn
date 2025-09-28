import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from .config import get_config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Configure CORS for production and development
    if config_name == "production":
        # Production: Allow specific domains and Netlify
        CORS(app, origins=[
            "https://neurolearn1.netlify.app",
            "https://neurolearn.netlify.app", 
            "https://*.netlify.app",
            "https://neurolearn-frontend.onrender.com",
            "https://neurolearn-dashboard.onrender.com"
        ])
    else:
        # Development: Allow localhost and specific domains
        CORS(app, origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://neurolearn1.netlify.app",
            "https://*.netlify.app"
        ])
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.emotion import emotion_bp
    from .routes.settings import settings_bp
    from .routes.recommendations import recommendations_bp
    from .routes.performance import performance_bp, quiz_bp
    from .routes.spaced_repetition import spaced_bp
    from .routes.feedback import feedback_bp
    from .routes.learning_dna import dna_bp
    from .routes.learning_style import style_bp
    from .routes.revision import revision_bp
    from .routes.gamification import gamification_bp
    from .routes.quests import quests_bp
    from .routes.personalization import personalization_bp
    from .routes.story import story_bp
    from .routes.sandbox import sandbox_bp
    from .routes.knowledge_graph import kg_bp
    from .routes.colearner import co_bp
    from .routes.curriculum import curriculum_bp
    from .routes.debate import debate_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(emotion_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    app.register_blueprint(performance_bp, url_prefix="/api/performance")
    app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
    app.register_blueprint(spaced_bp, url_prefix="/api/spaced")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(dna_bp, url_prefix="/api/dna")
    app.register_blueprint(style_bp, url_prefix="/api/learning-style")
    app.register_blueprint(revision_bp, url_prefix="/api/revision")
    app.register_blueprint(gamification_bp, url_prefix="/api/gamification")
    app.register_blueprint(quests_bp, url_prefix="/api/quests")
    app.register_blueprint(personalization_bp, url_prefix="/api/personalization")
    app.register_blueprint(story_bp, url_prefix="/api/story")
    app.register_blueprint(sandbox_bp, url_prefix="/api/sandbox")
    app.register_blueprint(kg_bp, url_prefix="/api/knowledge-graph")
    app.register_blueprint(co_bp, url_prefix="/api/colearner")
    app.register_blueprint(curriculum_bp, url_prefix="/api/curriculum")
    app.register_blueprint(debate_bp, url_prefix="/api/debate")

    # Create tables if not exist (dev convenience)
    with app.app_context():
        db.create_all()
        
        # Seed sample content for demo
        from .services.content_seeder import seed_sample_content
        seed_sample_content()
        
        # Seed badges for gamification
        from .services.badge_seeder import seed_badges
        seed_badges()
        
        # Seed story data
        from .services.story_seeder import seed_sample_story, seed_additional_badges
        seed_sample_story()
        seed_additional_badges()
        
        # Start curriculum scheduler
        from .services.curriculum_scheduler import curriculum_scheduler
        curriculum_scheduler.start()

    return app


