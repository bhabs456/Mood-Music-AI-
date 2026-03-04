import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

results = sp.search(q="love", limit=5, type="track", market="IN")

for track in results["tracks"]["items"]:
    print(track["name"], "-", track["artists"][0]["name"])