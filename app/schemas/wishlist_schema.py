from app.extensions import ma
from marshmallow import fields

class WishlistSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True,required=True)
    rawg_game_id = fields.Int(required=True)
    added_on = fields.DateTime(dump_only=True)

wishlist_items_schema = WishlistSchema(many=True)
wishlist_item_schema = WishlistSchema()