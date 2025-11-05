from flask import request, jsonify, Blueprint
from app.services import user_service
from app.extensions import db
from app.exceptions.exceptions import ValidationException
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    try:
        new_user = user_service.register_user(data)

        access_token = create_access_token(identity=new_user.id)
        return jsonify(access_token=access_token), 201
    except ValidationException as e:
        return jsonify({"error":e.message}), e.status_code

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "IntegrityError"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500

