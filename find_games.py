import json
import os

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
                found_games.append({'name': game_name, 'path': game_path})
    return found_games

def process_playlists():
    parsed_playlists = []

    with open('playlists.json', 'r') as file:
        data = json.load(file)

        if not data:
            return []

        for playlist in data:
            parsed_playlist = {}
            parsed_playlist['database'] = playlist['database']
            parsed_playlist['games'] = find_games_with_extension(playlist['roms'], playlist['extensions'])
            parsed_playlists.append(parsed_playlist)

    return parsed_playlists

for playlist in process_playlists():
    print(' ')
    print(playlist['database'])
    for game in playlist['games']:
        print(f"{game['name']} - {game['path']}")