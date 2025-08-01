from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import api_bp
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        # Import fetch_and_store_stocks here to avoid circular import
        from app.fetch_stocks import fetch_and_store_stocks
        fetch_and_store_stocks(app)

    return app
