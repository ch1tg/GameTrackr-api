import requests
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.services import game_service

bp = Blueprint('games', __name__, url_prefix='/games')


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
    try:
        page = request.args.get('page', 1, type=int)
        ordering = request.args.get('ordering', '-relevance')
        platform_id = request.args.get('platform')
    except ValueError:
        return jsonify({"error": "Invalid query parameters"}), 400

    try:
        data = game_service.get_trending_games(page, ordering, platform_id)
        return jsonify(data), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch from RAWG: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

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
    try:
        game_details = game_service.get_game_details(game_id)
        return jsonify(game_details), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({"error": "Game not found"}), 404
        return jsonify({"error": f"HTTP error: {str(e)}"}), e.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch from RAWG: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500