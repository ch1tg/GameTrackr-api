from sqlalchemy import ForeignKey, UniqueConstraint

from app.extensions import db

class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    rawg_game_id = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='wishlist_items')

    __table_args__ = (
        UniqueConstraint('user_id', 'rawg_game_id', name='_user_game_uc'),
    )

    def __repr__(self):
        return f'<Wishlist user_id={self.user_id} game_id={self.rawg_game_id}>'
