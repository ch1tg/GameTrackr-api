from flask import request, jsonify, Blueprint
from app.services import user_service
from app.extensions import db
from app.exceptions.exceptions import ValidationException
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_jwt_extended import jwt_required
from app.schemas.user_schema import user_default_schema, user_public_schema

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/<string:username>', methods=['GET'])
def get_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_public_schema.dump(user)), 200