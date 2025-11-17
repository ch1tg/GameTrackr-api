from flask import Blueprint, jsonify, request, current_app
from flasgger import swag_from
from app.services import search_service
from app.schemas.user_schema import  user_search_schema

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('', methods=['GET'])
@swag_from({
    'tags': ['Search'],
    'summary': 'Universal search (Users + Games)',
    'parameters': [
        {'name': 'q', 'in': 'query', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'user_limit', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'default': 5}},
        {'name': 'game_limit', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'default': 5}}
    ],
    'responses': {
        200: {'description': 'Aggregated search results'},
        400: {'description': 'Missing query parameter "q"'},
        500: {'description': 'RAWG API key missing or other internal error'}
    }
})
def search_all():
    q = request.args.get('q')
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        user_limit = request.args.get('user_limit', 5, type=int)
        game_limit = request.args.get('game_limit', 5, type=int)
    except ValueError:
        return jsonify({"error": "Invalid limit parameters"}), 400

    try:
        results = search_service.search_all(q, user_limit, game_limit)
        users_json = user_search_schema.dump(results['users'], many=True)

        return jsonify({
            "users": users_json,
            "games": results['games']
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in /search: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@bp.route('/users', methods=['GET'])
@swag_from({
    'tags': ['Search'],
    'summary': 'Paginated search for Users',
    'parameters': [
        {'name': 'q', 'in': 'query', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'page', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'default': 1}},
        {'name': 'limit', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'default': 20}}
    ],
    'responses': {
        200: {'description': 'Paginated user search results'},
        400: {'description': 'Missing query parameter "q"'}
    }
})
def search_users():
    q = request.args.get('q')
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    results = search_service.search_users(q, page, limit)

    users_json = user_search_schema.dump(results['users'], many=True)
    return jsonify({
        "users": users_json,
        "total_count": results['total_count'],
        "current_page": results['current_page'],
        "total_pages": results['total_pages']
    }), 200


@bp.route('/games', methods=['GET'])
@swag_from({
    'tags': ['Search'],
    'summary': 'Paginated search for Games (from RAWG)',
    'parameters': [
        {'name': 'q', 'in': 'query', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'page', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'default': 1}},
        {'name': 'limit', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'default': 20}}
    ],
    'responses': {
        200: {'description': 'Paginated game search results'},
        400: {'description': 'Missing query parameter "q"'},
        500: {'description': 'RAWG API key missing or other internal error'}
    }
})
def search_games():
    q = request.args.get('q')
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    try:
        results_object = search_service.search_games(q, page, limit)
        return jsonify(results_object), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Неожиданная ошибка в /search/games: {e}")
        return jsonify({"error": "Internal Server Error"}), 500