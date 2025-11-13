import requests
from flask import Blueprint, jsonify, current_app

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
        params = {
            'key': api_key,
            'page_size': 24,
        }


        response = requests.get('https://api.rawg.io/api/games', params=params, timeout=10)
        response.raise_for_status()

        raw_data = response.json()


        games = [transform_rawg_game_preview(game) for game in raw_data.get('results', [])]

        return jsonify(games), 200

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"RAWG API Error: {e.response.status_code}"}), e.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch from RAWG: {str(e)}"}), 503