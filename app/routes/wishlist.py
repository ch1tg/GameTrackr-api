from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app.exceptions.exceptions import ValidationException
from app.schemas.wishlist_schema import wishlist_items_schema, wishlist_item_schema
from app.services import wishlist_service
from app.extensions import db

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

@bp.route('/', methods=['GET'])
@jwt_required()
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

