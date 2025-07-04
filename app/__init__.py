from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    # Importa los modelos (¡IMPORTANTE!)

    # Importa y registra los Blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Crea las tablas
    with app.app_context():
        db.create_all()

    return app
