from flask_jwt_extended import create_access_token

from app.models.user import User
from app.extensions import db
from app.schemas.user_schema import user_default_schema, user_public_schema, user_login_schema
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
    return db.session.get(User, user_id)

def get_user_by_username(username):
    return db.session.query(User).filter_by(username=username).first()
'''
# --- 4. Обновление (Update) ---
def update_user_profile(user_id, data_to_update):

def change_user_password(user_id, data):

# --- 5. Удаление (Delete) ---
def delete_user_account(user_id, data):
'''