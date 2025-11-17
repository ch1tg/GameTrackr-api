from app.extensions import ma
from marshmallow import fields, validate, ValidationError, validates_schema

class UserSchema(ma.Schema):

    id = fields.Int(dump_only=True)
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, error="Username must be at least 3 characters long."),
            validate.Length(max=20, error="Username must be at most 20 characters long."),
            validate.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                error="Username must contain only letters, numbers and underscores.",
            )
        ]

    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True,
        validate=[
            validate.Length(min=8, error="Password must be at least 8 characters long."),
            validate.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                error="Password must contain only letters, numbers and underscores.",
            )
        ]
    )
    registered_on = fields.DateTime(dump_only=True)

class UserLoginSchema(ma.Schema):
    username = fields.Str()
    email = fields.Email()
    password = fields.Str(required=True, load_only=True)

    @validates_schema
    def check_for_username_or_email(self, data, **kwargs):
        username = data.get("username")
        email = data.get("email")
        if not username and not email:
            raise ValidationError("Field username or email is required",field_name="_schema")

class UserUpdateSchema(ma.Schema):
    username = fields.Str(
        validate=[
            validate.Length(min=3, error="Username must be at least 3 characters long."),
            validate.Length(max=20, error="Username must be at most 20 characters long."),
            validate.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                error="Username must contain only letters, numbers and underscores.",
            )
        ]

    )
    email = fields.Email()

class UserUpdatePassSchema(ma.Schema):
    old_password = fields.Str(required=True,load_only=True)
    new_password = fields.Str(
        required=True,
        load_only=True,
        validate=[
            validate.Length(min=8, error="Password must be at least 8 characters long."),
            validate.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                error="Password must contain only letters, numbers and underscores.",
            )
        ]
    )
class UserDeleteSchema(ma.Schema):
    password = fields.Str(required=True, load_only=True)

user_default_schema = UserSchema()
user_update_schema = UserUpdateSchema()
user_login_schema = UserLoginSchema()
user_update_password_schema = UserUpdatePassSchema()
user_delete_schema = UserDeleteSchema()
user_public_schema = UserSchema(exclude=("email",))
user_search_schema = UserSchema(only=("username",))
