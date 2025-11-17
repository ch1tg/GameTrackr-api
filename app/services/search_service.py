import requests
from requests import RequestException
from app.extensions import cache
from app.models.user import User
from flask import current_app
from app.utils.transformers import transform_rawg_game_preview

RAWG_API_URL = "https://api.rawg.io/api"

@cache.memoize(timeout=1200)
def search_games(q, page=1, limit=10):
    api_key = current_app.config.get('RAWG_API_KEY')
    if not api_key:
        current_app.logger.error("RAWG API key is not configured")
        raise ValueError("RAWG API key is not configured")

    params = {
        'key': api_key,
        'search': q,
        'page': page,
        'ordering': '-added',
        'page_size': limit
    }

    try:
        response = requests.get(
            f"{RAWG_API_URL}/games",
            params=params,
            timeout=5
        )
        response.raise_for_status()

        if response.status_code == 404:
            return {"games": [], "nextPage": None}

        data = response.json()
        raw_games = data.get('results', [])
        transformed_games = [transform_rawg_game_preview(game) for game in raw_games]
        has_next_page = data.get('next') is not None

        return {
            "games": transformed_games,
            "nextPage": page + 1 if has_next_page else None
        }

    except RequestException as e:
        current_app.logger.error(f"Ошибка при поиске игр в RAWG (q={q}): {e}")
        return {"games": [], "nextPage": None}


def search_users(q, page=1, limit=10):
    search_term = f"%{q}%"
    empty_result = {"users": [], "total_count": 0, "current_page": 1, "total_pages": 1}

    try:
        pagination_obj = User.query.filter(
            User.username.ilike(search_term)
        ).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )

        return {
            "users": pagination_obj.items,
            "total_count": pagination_obj.total,
            "current_page": page,
            "total_pages": pagination_obj.pages
        }
    except Exception as e:
        current_app.logger.error(f"Ошибка при поиске пользователей в БД (q={q}): {e}")
        return empty_result


def search_all(q, user_limit=10, game_limit=10):
    try:
        games_response = search_games(q, page=1, limit=game_limit)
        games_data = games_response.get("games", [])


    except ValueError as e:
        current_app.logger.error(f"Не удалось выполнить search_games: {e}")
        games_data = []


    users_data = search_users(q, page=1, limit=user_limit)

    return {
        "users": users_data.get("users", []),
        "games": games_data
    }