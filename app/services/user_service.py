from app.models.user import User
from app.extensions import db
from app.schemas.user_schema import user_register_schema, user_public_schema
from app.exceptions.exceptions import ValidationException
from marshmallow import ValidationError

'''# --- 1. Создание ---
def register_user(data):

def login_user(data):

# --- 3. Чтение (Read) ---
def get_user_by_id(user_id):

def get_user_by_username(username):

# --- 4. Обновление (Update) ---
def update_user_profile(user_id, data_to_update):

def change_user_password(user_id, data):

# --- 5. Удаление (Delete) ---
def delete_user_account(user_id, data):
'''