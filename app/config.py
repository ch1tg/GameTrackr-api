import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "None"

    RAWG_API_KEY = os.environ.get('RAWG_API_KEY')
    SWAGGER = {
        'openapi': '3.0.2',
        'info': {
            'title': 'GameTrackr API',
            'version': '1.0.0',
            'description': 'The official API documentation for the GameTrackr project.'
        },
        'uiversion': 3,
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                    'description': 'JWT Access Token. Format: "Bearer <token>"'
                },
                'csrfToken': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'X-CSRF-TOKEN',
                    'description': 'CSRF Token (from \'csrf_access_token\' cookie)'
                }
            }
        }
    }
