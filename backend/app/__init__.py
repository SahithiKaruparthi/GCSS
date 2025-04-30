from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from .routes.auth import auth_bp
from .routes.patient import patient_bp
from .routes.counselor import counselor_bp
from .routes.genetic_test import genetic_test_bp
from .routes.family_history import family_history_bp
from .routes.lifestyle_factor import lifestyle_factor_bp
from .routes.risk_report import risk_report_bp
from .routes.stats import stats_bp
from .utils.db import get_db_connection
from .utils.jwt import jwt
from .utils.mail import mail

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(counselor_bp)
    app.register_blueprint(genetic_test_bp)
    app.register_blueprint(family_history_bp)
    app.register_blueprint(lifestyle_factor_bp)
    app.register_blueprint(risk_report_bp)
    app.register_blueprint(stats_bp)

    return app