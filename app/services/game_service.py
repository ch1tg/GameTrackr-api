import requests
from flask import current_app
from app.extensions import cache
from app.utils.transformers import transform_rawg_game_preview, transform_rawg_game_details

@cache.memoize(timeout=1200)
def get_trending_games(page=1, ordering='-relevance', platform_id=None):

    api_key = current_app.config.get('RAWG_API_KEY')
    if not api_key:
        raise ValueError("RAWG API key is not configured")

    if page < 1:
        page = 1

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

    return {
        'games': games,
        'nextPage': page + 1 if has_next_page else None
    }

@cache.memoize(timeout=86400)
def _fetch_rawg_details_sync(game_id):
    api_key = current_app.config.get('RAWG_API_KEY')
    if not api_key:
        raise ValueError("RAWG API key is not configured")

    url = f'https://api.rawg.io/api/games/{game_id}'
    params = {'key': api_key}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()

def get_game_details(game_id):
    raw_data = _fetch_rawg_details_sync(game_id)
    return transform_rawg_game_details(raw_data)



def get_game_preview(game_id):
    raw_data = _fetch_rawg_details_sync(game_id)
    return transform_rawg_game_preview(raw_data)