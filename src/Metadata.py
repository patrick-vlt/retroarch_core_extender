from typing import List, Iterator

class Metadata:
    def __init__(self, name:str, summary:str, platforms:list = [], genres:list = [], release_dates:list = [], cover_url:str = None):
        self.name = name
        self.summary = summary
        self.platforms = platforms
        self.genres = genres
        self.release_dates = release_dates
        self.cover_url = cover_url

    def get_name(self) -> str:
        return self.name

    def get_summary(self) -> str:
        return self.summary

    def get_platforms(self) -> Iterator[str]:
        return self.platforms

    def get_genres(self) -> Iterator[str]:
        return self.genres

    def get_release_dates(self) -> Iterator[str]:
        return self.release_dates

    def get_cover_url(self) -> str:
        return self.cover_url