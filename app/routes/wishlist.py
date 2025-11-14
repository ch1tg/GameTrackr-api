from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app.exceptions.exceptions import ValidationException
from app.schemas.wishlist_schema import wishlist_items_schema, wishlist_item_schema
from app.services import wishlist_service
from app.extensions import db
from flasgger import swag_from

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

@bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Wishlist'],
    'summary': 'Get current user\'s wishlist',
    'security': [
        {'bearerAuth': []},
        {'csrfToken': []}
    ],
    'responses': {
        200: {
            'description': 'List of wishlist items',
            'content': {
                'application/json': {
                    'examples': {
                        'example': {
                            'summary': 'Success',
                            'value': [
                                {"id": 1, "user_id": 7, "rawg_game_id": 12345}
                            ]
                        }
                    }
                }
            }
        },
        400: {'description': 'Invalid user ID'},
        409: {'description': 'IntegrityError'},
        500: {'description': 'Internal Server Error'}
    }
})
def get_wishlist():
    user_id = get_jwt_identity()
    try:
        wishlist = wishlist_service.get_wishlist_by_userid(user_id)
        return jsonify(wishlist_items_schema.dump(wishlist)), 200
    except ValidationException as e:
        return jsonify({"error": e.message}), e.status_code
    except IntegrityError as e:
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Wishlist'],
    'summary': 'Add a game to the current user\'s wishlist',
    'security': [
        {'bearerAuth': []},
        {'csrfToken': []}
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'rawg_game_id': {'type': 'integer'}
                    },
                    'required': ['rawg_game_id']
                },
                'examples': {
                    'example': {
                        'value': { 'rawg_game_id': 12345 }
                    }
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Wishlist item created',
            'content': {
                'application/json': {
                    'examples': {
                        'example': {
                            'value': {"id": 2, "user_id": 7, "rawg_game_id": 12345}
                        }
                    }
                }
            }
        },
        400: {'description': 'Validation error'},
        409: {'description': 'IntegrityError'},
        500: {'description': 'Internal Server Error'}
    }
})
def add_to_wishlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        wishlist_item = wishlist_service.add_game_to_wishlist(user_id, data)
        return jsonify(wishlist_item_schema.dump(wishlist_item)), 201
    except ValidationException as e:
        return jsonify({"error": e.message}), e.status_code
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500






@bp.route('/<int:rawg_game_id>', methods=['DELETE']) # <-- 1. Принимаем ID из URL
@jwt_required()
@swag_from({
    'tags': ['Wishlist'],
    'summary': 'Remove a game from the current user\'s wishlist',
    'security': [
        {'bearerAuth': []},
        {'csrfToken': []}
    ],
    'parameters': [
        {
            'name': 'rawg_game_id', 'in': 'path', 'required': True,
            'schema': {'type': 'integer'}, 'description': 'RAWG game ID'
        },
    ],
    'responses': {
        204: {'description': 'Deleted'},
        404: {'description': 'Wishlist item not found'},
        409: {'description': 'IntegrityError'},
        500: {'description': 'Internal Server Error'}
    }
})
def delete_from_wishlist(rawg_game_id):
    user_id = get_jwt_identity()
    try:
        wishlist_service.delete_game_from_wishlist(user_id, rawg_game_id)
        return '', 204
    except ValidationException as e:
        return jsonify({"error": e.message}), e.status_code
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500


@bp.route('/', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Wishlist'],
    'summary': 'Reset current user\'s wishlist (delete all items)',
    'security': [
        {'bearerAuth': []},
        {'csrfToken': []}
    ],
    'responses': {
        204: {'description': 'All wishlist items deleted'},
        400: {'description': 'Invalid user ID'},
        409: {'description': 'IntegrityError'},
        500: {'description': 'Internal Server Error'}
    }
})
def reset_wishlist():
    user_id = get_jwt_identity()
    try:
        wishlist_service.reset_wishlist(user_id)
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

