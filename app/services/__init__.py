# app/__init__.py
# ... (imports from Part 1)

from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    api = Api(app)

    # Import and load models
    from app.services import prediction_service
    with app.app_context():
        prediction_service.load_models()
        prediction_service.self_test() # Optional self-test

    from app import routes
    routes.initialize_routes(api)

    return app