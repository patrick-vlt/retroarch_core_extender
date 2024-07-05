try:
    from dotenv import load_dotenv
    import requests
    import os
    import re
    import json
    import urllib.parse
    import webbrowser
    load_dotenv()
except ModuleNotFoundError:
    os.system('pip install requests')
    os.system('pip install python-dotenv')
    raise ModuleNotFoundError("Please restart the script")

def find_games_with_extension(directory, extension):
    found_games = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.' + extension):
                # Check the depth of the current root relative to the base directory
                path_parts = os.path.relpath(root, directory).split(os.sep)
                if len(path_parts) > 1:
                    # More than one level deep; use the first directory name under base as game name
                    game_name = path_parts[0]
                else:
                    # Directly in the base directory; use the file name
                    game_name = file.replace('.' + extension, '')

                game_path = os.path.join(root, file)
                game_name = re.split(r" \[|\s\(", game_name)[0]
                found_games.append({'name': game_name, 'path': game_path})

    return found_games

def map_games_from_playlists():
    playlists_with_game_paths = []

    with open('playlists.json', 'r') as file:
        data = json.load(file)

        if not data:
            return []

        for playlist in data:
            parsed_playlist = {}
            parsed_playlist['database'] = playlist['database']
            parsed_playlist['games'] = find_games_with_extension(playlist['roms'], playlist['extensions'])
            playlists_with_game_paths.append(parsed_playlist)

    return playlists_with_game_paths

def render_game_page(game, choice):
    # Generate the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{game['name']}</title>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-md-4">
                    <img src="{game['cover_url']}" class="img-fluid" alt="Game Cover">
                </div>
                <div class="col-md-8">
                    <h1>{game['name']}</h1>
                    <p><strong>Choice:</strong> {choice}</p>
                    <p><strong>Summary:</strong> {game['summary']}</p>
                    <p><strong>Platforms:</strong> {', '.join(game['platforms'])}</p>
                    <p><strong>Genres:</strong> {', '.join(game['genres'])}</p>
                    <p><strong>Release Dates:</strong> {', '.join(game['release_dates'])}</p>
                </div>
            </div>
        </div>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    """

    # Encode the HTML content using the urllib.parse.quote function
    encoded_html = urllib.parse.quote(html_content)

    # Construct the data URI
    data_uri = f"data:text/html;charset=utf-8,{encoded_html}"

    # Open the data URI in the default web browser
    webbrowser.open(data_uri)

def open_in_browser(url):
    webbrowser.open(url)

def generate_metadata_for_game(game):
    cover_url = game.get('cover', {}).get('url', None)
    if cover_url:
        cover_url = f"https:{cover_url.replace('t_thumb', 't_cover_big')}"

    metadata = {
        "name": game.get('name', 'N/A'),
        "summary": game.get('summary', 'N/A'),
        "platforms": [platform['name'] for platform in game.get('platforms', [])],
        "genres": [genre['name'] for genre in game.get('genres', [])],
        "release_dates": [date['human'] for date in game.get('release_dates', [])],
        "cover_url": cover_url
    }

    return metadata

def get_twitch_access_token(client_id, client_secret):
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

def scrape_game(client_id, access_token, game):
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
        return

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

    playlists_for_retroarch = []

    for playlist in map_games_from_playlists():
        for game in playlist['games']:
            game['metadata'] = scrape_game(client_id, access_token, game)

        playlists_for_retroarch.append({
            'database': playlist['database'],
            'games': playlist['games']
        })

    for playlist_info in playlists_for_retroarch:
        print(playlist_info['database'])
        for game in playlist_info['games']:
            print(game['name'])
            print(game['path'])
            print(game['metadata'])