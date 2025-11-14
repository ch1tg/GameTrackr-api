from flask import request, jsonify, Blueprint, current_app
from app.services import user_service
from app.services import wishlist_service
from app.exceptions.exceptions import ValidationException
from app.schemas.user_schema import user_default_schema, user_public_schema

import requests
from app.routes.games import transform_rawg_game_preview
from flasgger import swag_from

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/<string:username>', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get public profile by username',
    'parameters': [
        {
            'name': 'username', 'in': 'path', 'required': True,
            'schema': {'type': 'string'}, 'description': 'Username'
        }
    ],
    'responses': {
        200: {
            'description': 'User found',
            'content': {
                'application/json': {
                    'examples': {
                        'example': {
                            'value': {"id": 7, "username": "john_doe"}
                        }
                    }
                }
            }
        },
        404: {'description': 'User not found'}
    }
})
def get_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_public_schema.dump(user)), 200



@bp.route('/<string:username>/wishlist', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': "Get a user's wishlist previews",
    'parameters': [
        {'name': 'username', 'in': 'path', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'page', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'minimum': 1}},
        {'name': 'limit', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'minimum': 1, 'maximum': 100}}
    ],
    'responses': {
        200: {
            'description': 'Paginated wishlist previews',
            'content': {
                'application/json': {
                    'examples': {
                        'example': {
                            'value': {
                                'games': [
                                    { 'id': 12345, 'name': 'The Game', 'background_image': '...', 'metacritic': 88, 'parent_platforms': ['pc','xbox'] }
                                ],
                                'hasNextPage': True
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'User not found'},
        500: {'description': 'RAWG API key not configured or fetch error'}
    }
})
def get_user_wishlist(username):

    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 5, type=int)
        if page < 1: page = 1
        if limit < 1 or limit > 100: limit = 5
    except ValueError:
        page = 1
        limit = 5

    try:
        user = user_service.get_user_by_username(username)
        if user is None:
            return jsonify({"error": "User not found"}), 404

        pagination = wishlist_service.get_paginated_wishlist_by_userid(
            user_id=user.id,
            page=page,
            per_page=limit
        )

        rawg_ids = [item.rawg_game_id for item in pagination.items]
        has_next_page = pagination.has_next

        api_key = current_app.config.get('RAWG_API_KEY')
        if not api_key:
            return jsonify({"error": "RAWG API key not configured"}), 500

        games_preview_list = []
        for game_id in rawg_ids:
            try:
                url = f'https://api.rawg.io/api/games/{game_id}'
                params = {'key': api_key}
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                raw_data = response.json()

                game_preview = transform_rawg_game_preview(raw_data)
                games_preview_list.append(game_preview)
            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Failed to fetch game_id {game_id} from RAWG: {e}")
                pass

        return jsonify({
            "games": games_preview_list,
            "hasNextPage": has_next_page
        }), 200

    except ValidationException as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        # Общий "отлов"
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500