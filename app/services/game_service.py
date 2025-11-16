import requests
from flask import current_app
from app.extensions import cache

def _transform_rawg_game_preview(game):
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


def _transform_rawg_game_details(game):
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

@cache.memoize(timeout=1200, key_prefix="rawg_game")
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
    games = [_transform_rawg_game_preview(game) for game in raw_data.get('results', [])]
    has_next_page = raw_data.get('next') is not None

    return {
        'games': games,
        'nextPage': page + 1 if has_next_page else None
    }

@cache.memoize(timeout=86400, key_prefix="rawg_game_details") # <-- Можете оставить свой префикс
def _fetch_rawg_details_sync(game_id):
    """
    (Приватная) Кэшируемая 'базовая' функция.
    Получает "сырой" JSON из RAWG.
    """
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
    return _transform_rawg_game_details(raw_data)



def get_game_preview(game_id):
    raw_data = _fetch_rawg_details_sync(game_id)
    return _transform_rawg_game_preview(raw_data)