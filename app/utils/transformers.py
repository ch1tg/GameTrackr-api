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