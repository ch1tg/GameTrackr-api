import requests
from flask import Blueprint, jsonify, current_app, request

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