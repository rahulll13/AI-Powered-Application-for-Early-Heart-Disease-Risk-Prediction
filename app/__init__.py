# app/__init__.py

import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    api = Api(app)

    from .models import User

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        user = User.query.get(int(identity))
        if user:
            # --- THIS IS THE NEW DEBUG LINE ---
            print(f"DEBUG: Creating token for user '{user.username}'. Role found in DB: {user.role}")
            # -----------------------------------
            return {'role': user.role}
        return {'role': None}

    # The '/uploads/profile_pics/' route has been removed.

    with app.app_context():
        from app.services import prediction_service
        prediction_service.load_models()
    
    from app import routes
    routes.initialize_routes(api)
    return app