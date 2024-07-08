from typing import List, Iterator

from Game import *

import os
import re
import json

class Playlist:
    def __init__(self, database:str, roms:List[str] = [], extensions:List[str] = [], games:List[Game] = []):
        self.database = database
        self.roms = roms
        self.extensions = extensions
        self.games = games

    def get_database(self) -> str:
        return self.database

    def get_roms(self) -> List[str]:
        return self.roms

    def get_extensions(self) -> List[str]:
        return self.extensions

    def get_games(self) -> List[Game]:
        return self.games

    def remove_game(self, game:Game):
        self.games.remove(game)

    def set_games(self):
        if 'lutris' in self.get_extensions():
            self.games = self.__find_games_installed_in_lutris()
        else:
            self.games = self.__find_games_by_extension()

    def __find_games_installed_in_lutris(self) -> List[Game]:
        found_games = []

        try:
            response = os.popen('lutris -l --json').read()
            games = json.loads(response)
        except:
            print("Failed to get installed games from Lutris")
            return []

        print('Fetched installed games from Lutris. Processing...')

        for game in games:
            try:
                game = dict(game)
                found_games.append(
                    Game(
                        game['name'],
                        f"env LUTRIS_SKIP_INIT=1 lutris lutris:rungameid/{game['id']}"
                    )
                )
            except:
                continue

        return found_games

    def __find_games_by_extension(self, playlist:list) -> List[Game]:
        found_games = []

        for root, dirs, files in os.walk(playlist['roms']):
            for file in files:
                for extension in playlist['extensions']:
                    if file.endswith('.' + extension):
                        # Check the depth of the current root relative to the base directory
                        path_parts = os.path.relpath(root, playlist['roms']).split(os.sep)

                        if len(path_parts) > 1:
                            # More than one level deep; use the first directory name under base as game name
                            game_name = path_parts[0]
                        else:
                            # Directly in the base directory; use the file name
                            game_name = file.replace('.' + playlist['roms'], '')

                        game_path = os.path.join(root, file)
                        game_name = re.split(r" \[|\s\(", game_name)[0]
                        game_name = game_name.replace(f".{extension}", '')
                        found_games.append(Game(game_name, game_path))

        return found_games