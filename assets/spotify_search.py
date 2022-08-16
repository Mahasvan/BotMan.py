import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from assets import time_assets

class Spotify:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.track_id_regex = r"(?<=\/track\/)([a-zA-Z0-9]*?)(?=\?|$0|\>)"
        self.playlist_id_regex = r"(?<=\/playlist\/)([a-zA-Z0-9]*?)(?=\?|$0|\>)"
        self.album_id_regex = r"(?<=\/album\/)([a-zA-Z0-9]*?)(?=\?|$0|\>)"
        self.artist_id_regex = r"(?<=\/artist\/)([a-zA-Z0-9]*?)(?=\?|$0|\>)"
        try:
            self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                                                 client_secret=client_secret))
        except spotipy.SpotifyOauthError:
            print("Spotify credentials invalid! Please check your credentials and try again.")
            exit(0)

    def search_artist(self, search_term: str):
        if re.findall(self.artist_id_regex, str(search_term)):
            artist_id = re.findall(self.artist_id_regex, str(search_term))[0]
            try:
                items = [self.spotify.artist(artist_id)]
            except spotipy.SpotifyException:
                raise ValueError
        else:
            results = self.spotify.search(q=f"artist:{search_term}", type="artist")
            items = results['artists']['items']

        if len(items) == 0:
            raise ValueError
        name = items[0].get("name")
        artist_url = items[0].get("external_urls").get("spotify")
        followers = items[0].get("followers").get("total")
        genres = items[0].get("genres")
        genres.sort()
        artist_id = items[0].get("id")
        picture = items[0].get("images")[0].get("url")

        return name, artist_id, artist_url, picture, genres, followers

    def artist_results(self, search_term: str):
        if re.findall(self.artist_id_regex, str(search_term)):
            artist_id = re.findall(self.artist_id_regex, str(search_term))[0]
            try:
                items = [self.spotify.artist(artist_id)]
            except spotipy.SpotifyException:
                raise ValueError
        else:
            results = self.spotify.search(q=f"artist:{search_term}", type="artist")
            items = results['artists']['items']

        result_dict = {}
        if len(items) == 0:
            raise ValueError
        for x in range(len(items)):
            name = items[x].get("name")
            artist_url = items[x].get("external_urls").get("spotify")
            result_dict[name] = artist_url
        top_artist = {"name": items[0].get("name"), "url": items[0].get("external_urls").get("spotify"),
                      "picture": items[0].get("images")[0].get("url")}

        return result_dict, top_artist

    def get_artist_top_track(self, artist_id: str):
        artist_top_songs = self.spotify.artist_top_tracks(artist_id)
        artist_top_songs = artist_top_songs.get("tracks")[0]

        track_name = (artist_top_songs.get("album").get("name"))
        track_url = (artist_top_songs.get("external_urls").get("spotify"))
        return track_name, track_url

    def get_artist_tracks(self, artist_id: str):
        artist_top_songs = self.spotify.artist_top_tracks(artist_id)
        result_dict = {}
        for x in range(len(artist_top_songs)):
            artist_top_songs = artist_top_songs.get("tracks")[x]

            track_name = (artist_top_songs.get("album").get("name"))
            track_url = (artist_top_songs.get("external_urls").get("spotify"))
            result_dict[track_name] = track_url
        return result_dict

    def get_related_artist(self, artist_id: str):
        artists = self.spotify.artist_related_artists(artist_id=artist_id)
        return_list = []
        for x in artists.get("artists")[:4]:
            return_list.append({x.get("name"): x.get("external_urls").get("spotify")})

        return return_list

    def search_album(self, search_term: str):
        if re.findall(self.album_id_regex, str(search_term)):
            album_id = re.findall(self.album_id_regex, str(search_term))[0]
            try:
                album_info = self.spotify.album(album_id)
            except spotipy.SpotifyException:
                raise ValueError
        else:
            result = self.spotify.search(q=search_term, type="album")
            result = result.get("albums")
            albums_list = list(result.get("items"))
            if len(albums_list) == 0:
                raise ValueError
            album_info = albums_list[0]

        artist_dict = {}
        for artist in album_info.get("artists"):
            artist_name = artist.get("name")
            spot_url = artist.get("external_urls").get("spotify")
            artist_dict[artist_name] = spot_url
        album_url = album_info.get("external_urls").get("spotify")
        album_name = album_info.get("name")
        release_date = time_assets.format_date_yyyymmdd(album_info.get("release_date"))
        total_tracks = album_info.get("total_tracks")
        markets = len(album_info.get("available_markets"))
        thumbnail = album_info.get("images")[0].get("url")
        album_id = album_info.get("id")
        return album_name, album_url, album_id, artist_dict, total_tracks, release_date, markets, thumbnail

    def search_track(self, search_term: str):
        if re.findall(self.track_id_regex, str(search_term)):
            track_id = re.findall(self.track_id_regex, str(search_term))[0]
            try:
                track_info = self.spotify.track(track_id)
            except spotipy.SpotifyException:
                raise ValueError
        else:
            result = self.spotify.search(q=search_term, type="track", limit=1)
            result = result.get("tracks")
            tracks_list = list(result.get("items"))
            if len(tracks_list) == 0:
                raise ValueError
            track_info = tracks_list[0]

        artist_dict = {}
        for artist in track_info.get("artists"):
            artist_name = artist.get("name")
            spot_url = artist.get("external_urls").get("spotify")
            artist_dict[artist_name] = spot_url
        track_url = track_info.get("external_urls").get("spotify")
        track_name = track_info.get("name")
        track_id = track_info.get("id")
        icon_url = track_info["album"]["images"][0]["url"]
        release_date = time_assets.format_date_yyyymmdd(track_info["album"]["release_date"])
        available_markets = len(track_info.get("available_markets"))
        popularity = track_info.get("popularity")

        return track_name, track_url, track_id, artist_dict, icon_url, release_date, available_markets, popularity
