from app.extensions import ma
from marshmallow import fields, validate

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
    created_at = fields.DateTime(dump_only=True)

user_register_schema = UserSchema()
user_public_schema = UserSchema(exclude=("email",))
