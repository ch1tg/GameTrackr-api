from flask import request, jsonify, Blueprint
from app.services import user_service
from app.extensions import db
from app.exceptions.exceptions import ValidationException
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity, set_access_cookies, unset_access_cookies
from flask_jwt_extended import jwt_required
from app.schemas.user_schema import user_default_schema
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    try:
        new_user = user_service.register_user(data)

        access_token = create_access_token(identity=str(new_user.id))
        response = jsonify(user_default_schema.dump(new_user))
        set_access_cookies(response, access_token)
        return response, 201
    except ValidationException as e:
        return jsonify({"error":e.message}), e.status_code

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    try:
        user = user_service.login_user(data)
        access_token = create_access_token(identity=str(user.id))
        response = jsonify(user_default_schema.dump(user))
        set_access_cookies(response, access_token)
        return response, 200

    except ValidationException as e:
        return jsonify({"error":e.message}), e.status_code

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_access_cookies(response)
    return response, 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = user_service.get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_default_schema.dump(user)), 200

@bp.route('/me', methods=['PATCH'])
@jwt_required()
def me_patch():
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        updated_user=user_service.update_user_profile(user_id, data)
        return jsonify(user_default_schema.dump(updated_user)), 200
    except ValidationException as e:
        db.session.rollback()
        return jsonify({"error":e.message}), e.status_code
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500


@bp.route('/me/password', methods=['PUT'])
@jwt_required()
def me_password():
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        updated_user=user_service.change_user_password(user_id, data)
        return jsonify(user_default_schema.dump(updated_user)), 200
    except ValidationException as e:
        db.session.rollback()
        return jsonify({"error":e.message}), e.status_code
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

@bp.route('/me', methods=['DELETE'])
@jwt_required()
def me_delete():
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        user_service.delete_user_account(user_id, data)
        return '', 204
    except ValidationException as e:
        db.session.rollback()
        return jsonify({"error": e.message}), e.status_code
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

