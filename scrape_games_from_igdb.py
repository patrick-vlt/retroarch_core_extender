from src.Game import Game
from src.Playlist import Playlist
from src.Metadata import Metadata

from typing import List, Iterator, Optional

try:
    from dotenv import load_dotenv
    import requests
    import os
    import json

    load_dotenv()
except ModuleNotFoundError:
    os.system('pip install requests --break-system-packages')
    os.system('pip install python-dotenv --break-system-packages')
    raise ModuleNotFoundError("Please restart the script")

def map_games_from_playlists() -> List[Playlist]:
    playlists = []

    with open('playlists.json', 'r') as playlists_json_raw:
        playlists_json = json.load(playlists_json_raw)

        if not playlists_json:
            return []

        for playlist_json in playlists_json:
            playlist = Playlist(
                playlist_json['database'],
                playlist_json['roms'],
                playlist_json['extensions'],
            )
            playlist.set_games()
            playlists.append(playlist)

    return playlists

def generate_metadata_for_game(game):
    cover_url = game.get('cover', {}).get('url', None)

    if cover_url:
        cover_url = f"https:{cover_url.replace('t_thumb', 't_cover_big')}"

    return Metadata(
        game.get('name', 'N/A'),
        game.get('summary', 'N/A'),
        [platform['name'] for platform in game.get('platforms', [])],
        [genre['name'] for genre in game.get('genres', [])],
        [date['human'] for date in game.get('release_dates', [])],
        cover_url
    )

def get_twitch_access_token(client_id:str, client_secret:str) -> str:
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)

    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print(f"Failed to get access token: {response.status_code}")
        print(response.json())
        return None

def scrape_game(client_id:str, access_token:str, game:Game) -> Optional[Metadata]:
    print(f"\nScraping game: {game['name']}...\n")

    url = 'https://api.igdb.com/v4/games'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
    }
    data = f'search "{game['name']}"; fields name,cover.url,summary,platforms.name,genres.name,release_dates.human; limit 20;'
    response = requests.post(url, headers=headers, data=data)
    games = response.json()

    if not games:
        print(f"No games found by title: {game['name']}")
        return None

    print("Found the following games:\n")
    for i, game in enumerate(games):
        choice = i+1
        metadata = generate_metadata_for_game(game)
        print(f"{choice}: {metadata['name']}")
        # render_game_page(metadata, choice)

    print("\n")

    if len(games) == 1:
        choice = 0
    else:
        # choice = int(input("Enter the number of the game you wish to scrape.")) - 1
        choice = 0

    if choice < 0 or choice >= len(games):
        print("Invalid choice")
        return

    return metadata

if __name__ == "__main__":
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    access_token = get_twitch_access_token(client_id, client_secret)

    if access_token:
        print(f"Access Token: {access_token}")

    playlists = map_games_from_playlists()

    for playlist in playlists:
        for game in playlist.get_games():
            game.set_metadata(scrape_game(client_id, access_token, game))

            if game.get_metadata():
                continue

            playlist.remove_game(game)

    for playlist_info in playlists:
        print(playlist_info['database'])
        for game in playlist_info['games']:
            print(game['name'])
            print(game['path'])
            try:
                if game['metadata']:
                    print(game['metadata'])
            except:
                pass