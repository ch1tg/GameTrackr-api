import requests
from flask import Blueprint, jsonify, current_app, request
from flasgger import swag_from

bp = Blueprint('games', __name__, url_prefix='/games')

def transform_rawg_game_preview(game):
    platforms = []
    if game.get('parent_platforms'):
        platforms = [
            p.get('platform', {}).get('slug')
            for p in game.get('parent_platforms', [])
            if p.get('platform')
        ]

    return {
        'id': game.get('id'),
        'name': game.get('name'),
        'background_image': game.get('background_image'),
        'metacritic': game.get('metacritic'),
        'parent_platforms': platforms
    }



@bp.route('/trending', methods=['GET'])
@swag_from({
    'tags': ['Games'],
    'summary': 'Get trending games from RAWG with optional filters',
    'parameters': [
        {'name': 'page', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1}, 'required': False},
        {'name': 'ordering', 'in': 'query', 'schema': {'type': 'string'}, 'required': False, 'description': 'RAWG ordering, e.g. -relevance'},
        {'name': 'platform', 'in': 'query', 'schema': {'type': 'string'}, 'required': False, 'description': 'RAWG platform id'}
    ],
    'responses': {
        200: {
            'description': 'Trending games page',
            'content': {
                'application/json': {
                    'examples': {
                        'example': {
                            'value': {
                                'games': [
                                    { 'id': 123, 'name': 'Foo', 'background_image': '...', 'metacritic': 90, 'parent_platforms': ['pc'] }
                                ],
                                'nextPage': 2
                            }
                        }
                    }
                }
            }
        },
        500: {'description': 'RAWG API key missing or upstream error'},
        503: {'description': 'Failed to fetch from RAWG'}
    }
})
def get_trending_games():
    api_key = current_app.config.get('RAWG_API_KEY')
    if not api_key:
        return jsonify({"error": "RAWG API key is not configured"}), 500

    try:

        page = request.args.get('page', 1, type=int)

        ordering = request.args.get('ordering', '-relevance')

        platform_id = request.args.get('platform')

        if page < 1:
            page = 1

    except ValueError:
        page = 1
        ordering = '-relevance'
        platform_id = None

    try:
        params = {
            'key': api_key,
            'page_size': 24,
            'page': page,
            'ordering': ordering
        }

        if platform_id:
            params['platforms'] = platform_id

        response = requests.get('https://api.rawg.io/api/games', params=params, timeout=10)
        response.raise_for_status()

        raw_data = response.json()
        games = [transform_rawg_game_preview(game) for game in raw_data.get('results', [])]
        has_next_page = raw_data.get('next') is not None

        return jsonify({
            'games': games,
            'nextPage': page + 1 if has_next_page else None
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch from RAWG: {str(e)}"}), 503


def transform_rawg_game_details(game):

    genres = [g.get('name') for g in game.get('genres', []) if g.get('name')]
    platforms = []
    if game.get('platforms'):
        platforms = [p.get('platform', {}).get('name') for p in game.get('platforms', []) if p.get('platform')]

    return {
        'id': game.get('id'),
        'name': game.get('name'),
        'description': game.get('description'),
        'metacritic': game.get('metacritic'),
        'released': game.get('released'),
        'background_image': game.get('background_image'),
        'website': game.get('website'),
        'genres': genres,
        'platforms': platforms,
    }



@bp.route('/<int:game_id>', methods=['GET'])
@swag_from({
    'tags': ['Games'],
    'summary': 'Get detailed RAWG game info by id',
    'parameters': [
        {'name': 'game_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}
    ],
    'responses': {
        200: {
            'description': 'Game details',
            'content': {
                'application/json': {
                    'examples': {
                        'example': {
                            'value': {
                                'id': 123,
                                'name': 'Foo',
                                'description': '<p>HTML description</p>',
                                'metacritic': 90,
                                'released': '2020-01-01',
                                'background_image': '...',
                                'website': 'https://example.com',
                                'genres': ['Action'],
                                'platforms': ['PC']
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'Game not found'},
        500: {'description': 'RAWG API key missing or HTTP error'},
        503: {'description': 'Failed to fetch from RAWG'}
    }
})
def get_game_details(game_id):
    api_key = current_app.config.get('RAWG_API_KEY')
    if not api_key:
        return jsonify({"error": "RAWG API key is not configured"}), 500

    try:

        url = f'https://api.rawg.io/api/games/{game_id}'
        params = {'key': api_key}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

        game_details = transform_rawg_game_details(raw_data)

        return jsonify(game_details), 200

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({"error": "Game not found"}), 404
        return jsonify({"error": f"HTTP error: {str(e)}"}), e.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch from RAWG: {str(e)}"}), 503