from flask import Flask
from .config import Config
from flask_cors import CORS
from .extensions import db, ma, migrate, jwt, swagger

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(
        app,
        origins=["http://localhost:5173"],
        supports_credentials=True
    )
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    # Ensure Flasgger uses our OpenAPI 3 template so requestBody is rendered
    swagger.template = app.config.get('SWAGGER')
    swagger.init_app(app)

    from . import models

    from .routes import auth
    app.register_blueprint(auth.bp)
    from .routes import users
    app.register_blueprint(users.bp)
    from .routes import games
    app.register_blueprint(games.bp)
    from .routes import wishlist
    app.register_blueprint(wishlist.bp)

    return app
