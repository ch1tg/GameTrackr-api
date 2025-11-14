from app.models import Wishlist
from app.extensions import db
from app.exceptions.exceptions import ValidationException
from marshmallow import ValidationError

from app.schemas.wishlist_schema import wishlist_item_schema


def get_wishlist_by_userid(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user ID", status_code=400)


    wishlist_items = Wishlist.query.filter_by(user_id=uid).all()
    return wishlist_items


def add_game_to_wishlist(user_id,data):
    try:
        validated_data = wishlist_item_schema.load(data)
    except ValidationError as e:
        raise ValidationException(e.messages, status_code=400)
    wishlist_item = Wishlist(
        user_id=user_id,
        rawg_game_id=validated_data['rawg_game_id']
    )

    db.session.add(wishlist_item)
    db.session.commit()

    return wishlist_item


def delete_game_from_wishlist(user_id, rawg_game_id):
    item = Wishlist.query.filter_by(
        user_id=user_id,
        rawg_game_id=rawg_game_id
    ).first()

    if item is None:
        raise ValidationException("Wishlist item not found", status_code=404)

    db.session.delete(item)
    db.session.commit()
    return True


def get_paginated_wishlist_by_userid(user_id, page=1, per_page=5):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user ID", status_code=400)
    pagination = Wishlist.query.filter_by(user_id=uid) \
        .order_by(Wishlist.added_on.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    if not pagination.items and page > 1:

        raise ValidationException("Page not found", status_code=404)

    return pagination


def reset_wishlist(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        raise ValidationException("Invalid user ID", status_code=400)

    Wishlist.query.filter_by(user_id=uid).delete()
    db.session.commit()
    return True
