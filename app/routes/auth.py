from flask import request, jsonify, Blueprint
from app.services import user_service
from app.extensions import db
from app.exceptions.exceptions import ValidationException
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity, set_access_cookies, unset_access_cookies
from flask_jwt_extended import jwt_required
from app.schemas.user_schema import user_default_schema
from flasgger import swag_from
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Register a new user and issue an access token',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string', 'minLength': 3, 'maxLength': 20},
                        'email': {'type': 'string', 'format': 'email'},
                        'password': {'type': 'string', 'minLength': 8}
                    },
                    'required': ['username', 'email', 'password']
                },
                'examples': {
                    'example': {
                        'value': { 'username': 'john_doe', 'email': 'john@example.com', 'password': 'Pass_w0rd' }
                    }
                }
            }
        }
    },
    'responses': {
        201: {'description': 'User created and cookie set with access token'},
        400: {'description': 'Validation error'},
        409: {'description': 'IntegrityError or duplicate username/email'},
        500: {'description': 'Internal Server Error'}
    }
})
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
@swag_from({
    'tags': ['Auth'],
    'summary': 'Login and issue an access token',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'oneOf': [
                        {
                            'type': 'object',
                            'properties': {
                                'username': {'type': 'string'},
                                'password': {'type': 'string'}
                            },
                            'required': ['username', 'password']
                        },
                        {
                            'type': 'object',
                            'properties': {
                                'email': {'type': 'string', 'format': 'email'},
                                'password': {'type': 'string'}
                            },
                            'required': ['email', 'password']
                        }
                    ]
                },
                'examples': {
                    'byUsername': { 'value': { 'username': 'john_doe', 'password': 'Pass_w0rd' } },
                    'byEmail': { 'value': { 'email': 'john@example.com', 'password': 'Pass_w0rd' } }
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Logged in and cookie set with access token'},
        400: {'description': 'Validation error or missing username/email'},
        401: {'description': 'Invalid credentials'},
        409: {'description': 'IntegrityError'},
        500: {'description': 'Internal Server Error'}
    }
})
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

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Auth'],
    'summary': 'Logout and clear access cookies',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'X-CSRF-TOKEN', 'in': 'header', 'required': True,
            'schema': {'type': 'string'},
            'description': 'CSRF token from csrf_access_token cookie (required when authenticating via cookies)'
        }
    ],
    'responses': {
        200: {'description': 'Logout successful'}
    }
})
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_access_cookies(response)
    return response, 200

@bp.route('/me', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Auth'],
    'summary': 'Get current user profile',
    'security': [{'bearerAuth': []}],
    'responses': {
        200: {'description': 'Current user profile'},
        404: {'description': 'User not found'}
    }
})
def me():
    user_id = get_jwt_identity()
    user = user_service.get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_default_schema.dump(user)), 200

@bp.route('/me', methods=['PATCH'])
@jwt_required()
@swag_from({
    'tags': ['Auth'],
    'summary': 'Update current user profile',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'X-CSRF-TOKEN', 'in': 'header', 'required': True,
            'schema': {'type': 'string'},
            'description': 'CSRF token from csrf_access_token cookie (required when authenticating via cookies)'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string', 'minLength': 3, 'maxLength': 20},
                        'email': {'type': 'string', 'format': 'email'}
                    }
                },
                'examples': {
                    'example': { 'value': { 'username': 'new_name' } }
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Profile updated'},
        400: {'description': 'Validation error'},
        409: {'description': 'IntegrityError or duplicate username/email'},
        500: {'description': 'Internal Server Error'}
    }
})
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
@swag_from({
    'tags': ['Auth'],
    'summary': 'Change current user password',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'X-CSRF-TOKEN', 'in': 'header', 'required': True,
            'schema': {'type': 'string'},
            'description': 'CSRF token from csrf_access_token cookie (required when authenticating via cookies)'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'old_password': {'type': 'string', 'minLength': 8},
                        'new_password': {'type': 'string', 'minLength': 8}
                    },
                    'required': ['old_password', 'new_password']
                },
                'examples': {
                    'example': { 'value': { 'old_password': 'Pass_w0rd', 'new_password': 'New_Pass1' } }
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Password changed'},
        400: {'description': 'Validation error'},
        403: {'description': 'Invalid old password'},
        409: {'description': 'New password equals old'},
        500: {'description': 'Internal Server Error'}
    }
})
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
@swag_from({
    'tags': ['Auth'],
    'summary': 'Delete current user account',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'X-CSRF-TOKEN', 'in': 'header', 'required': True,
            'schema': {'type': 'string'},
            'description': 'CSRF token from csrf_access_token cookie (required when authenticating via cookies)'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'password': {'type': 'string', 'minLength': 8}
                    },
                    'required': ['password']
                },
                'examples': {
                    'example': { 'value': { 'password': 'Pass_w0rd' } }
                }
            }
        }
    },
    'responses': {
        204: {'description': 'Account deleted'},
              400: {'description': 'Validation error'},
        403: {'description': 'Invalid password'},
        404: {'description': 'User not found'},
        409: {'description': 'IntegrityError'},
        500: {'description': 'Internal Server Error'}
    }
})
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

