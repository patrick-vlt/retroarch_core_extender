from typing import List, Iterator
import webbrowser
import urllib.parse

from Metadata import *

class Game:
    def __init__(self, name:str, path:str, metadata:List[Metadata] = []):
        self.name = name
        self.path = path
        self.metadata = metadata

    def get_name(self) -> str:
        return self.name

    def get_path(self) -> str:
        return self.path

    def get_metadata(self) -> Metadata:
        return self.metadata

    def set_metadata(self, metadata:Metadata):
        self.metadata = metadata

    def open_in_browser(url) -> None:
        webbrowser.open(url)

    def render_game_page(self, choice:int) -> None:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.get_name()}</title>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row">
                    <div class="col-md-4">
                        <img src="{self.get_metadata().get_cover_url()}" class="img-fluid" alt="Game Cover">
                    </div>
                    <div class="col-md-8">
                        <h1>{self.get_metadata().get_name()}</h1>
                        <p><strong>Choice:</strong> {choice}</p>
                        <p><strong>Summary:</strong> {self.get_metadata().get_summary()}</p>
                        <p><strong>Platforms:</strong> {', '.join(self.get_metadata().get_platforms())}</p>
                        <p><strong>Genres:</strong> {', '.join(self.get_metadata().get_genres())}</p>
                        <p><strong>Release Dates:</strong> {', '.join(self.get_metadata().get_release_dates())}</p>
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