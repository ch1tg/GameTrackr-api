from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.extensions import db
from app.schemas.user_schema import user_default_schema, user_update_password_schema, user_login_schema, \
    user_update_schema, user_delete_schema
from app.exceptions.exceptions import ValidationException
from marshmallow import ValidationError

# --- 1. Создание ---
def register_user(data):
    try:
        validated_data = user_default_schema.load(data)
    except ValidationError as e:
        raise ValidationException(e.messages, status_code=400)

    if db.session.query(User).filter_by(username=validated_data['username']).first():
        raise ValidationException("Username already exists", status_code=409)

    if db.session.query(User).filter_by(email=validated_data['email']).first():
        raise ValidationException("Email already exists", status_code=409)

    password = validated_data.pop('password')

    new_user = User(**validated_data)

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def login_user(data):
    try:
        validated_data = user_login_schema.load(data)
    except ValidationError as e:
        raise ValidationException(e.messages, status_code=400)

    password = validated_data['password']

    user=None
    if 'username' in validated_data:
        user = db.session.query(User).filter_by(username=validated_data['username']).first()
    elif 'email' in validated_data:
        user = db.session.query(User).filter_by(email=validated_data['email']).first()

    if user is None or not user.check_password(password):
        raise ValidationException("Invalid login data", status_code=401)

    access_token = create_access_token(identity=str(user.id))
    return access_token




def get_user_by_id(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user id", status_code=400)
    return db.session.get(User, uid)

def get_user_by_username(username):
    return db.session.query(User).filter_by(username=username).first()

def update_user_profile(user_id, data_to_update):
    # Ensure user_id is an integer (access token stores it as string)
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user id", status_code=400)

    user = db.session.get(User, uid)
    if user is None:
        raise ValidationException("User not found", status_code=404)

    try:
        validated_data = user_update_schema.load(data_to_update)
    except ValidationError as e:
        raise ValidationException(e.messages, status_code=400)

    if "username" in validated_data and validated_data["username"] != user.username:
        if db.session.query(User).filter_by(username=validated_data["username"]).first():
            raise ValidationException("Username already exists", status_code=409)
        user.username = validated_data["username"]

    if "email" in validated_data and validated_data["email"] != user.email:
        if db.session.query(User).filter_by(email=validated_data["email"]).first():
            raise ValidationException("Email already exists", status_code=409)
        user.email = validated_data["email"]

    db.session.commit()
    return user


def change_user_password(user_id, data):

    try:
        validated_data = user_update_password_schema.load(data)
    except ValidationError as e:
        raise ValidationException(e.messages, status_code=400)

    old_pass_plain = validated_data['old_password']
    new_pass_plain = validated_data['new_password']

    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user id", status_code=400)

    user = db.session.get(User, uid)
    if user is None:
        raise ValidationException("User not found", status_code=404)


    if not user.check_password(old_pass_plain):
        raise ValidationException("Invalid old password", status_code=403)

    if old_pass_plain == new_pass_plain:
        raise ValidationException("New password cannot be the same", status_code=409)


    user.set_password(new_pass_plain)

    db.session.commit()
    return user


def delete_user_account(user_id, data):
    try:
        validated_data = user_delete_schema.load(data)
    except ValidationError as e:
        raise ValidationException(e.messages, status_code=400)

    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user id", status_code=400)

    user = db.session.get(User, uid)
    if user is None:
        raise ValidationException("User not found", status_code=404)

    password = validated_data['password']

    if not user.check_password(password):
        raise ValidationException("Invalid password", status_code=403)

    db.session.delete(user)
    db.session.commit()

    return True