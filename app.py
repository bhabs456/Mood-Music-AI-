from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re
import spotipy

load_dotenv()

app = Flask(__name__)


from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Configure Gemini
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You are Sargam AI, a music recommendation assistant.

Your task is to recommend songs based on the user's mood.

Rules:
1. The mood will be provided by the system. Use it to recommend songs.
2. Recommend exactly 5 songs.
3. Include title and artist.
4. Do not add explanations.

Return the response ONLY in this JSON format:

{
 "mood": "Mood name",
 "songs": [
   {
     "title": "Song Name",
     "artist": "Artist Name"
   },
   {
     "title": "Song Name",
     "artist": "Artist Name"
   },
   {
     "title": "Song Name",
     "artist": "Artist Name"
   },
   {
     "title": "Song Name",
     "artist": "Artist Name"
   },
   {
     "title": "Song Name",
     "artist": "Artist Name"
   }
 ]
}
"""

print("API KEY:", os.getenv("GEMINI_API_KEY"))

def detect_mood(text):

    text = text.lower()

    mood_keywords = {

        "happy": [
            "happy","joy","joyful","great","excited","awesome","fantastic",
            "amazing","cheerful","glad","good mood","delighted"
        ],

        "sad": [
            "sad","cry","crying","lonely","depressed","heartbroken",
            "down","upset","hurt","gloomy","miserable"
        ],

        "romantic": [
            "love","romantic","crush","date","in love","relationship",
            "affection","missing someone"
        ],

        "energetic": [
            "energetic","gym","workout","running","party","dance",
            "hype","pumped","active","motivation"
        ],

        "focus": [
            "focus","study","studying","work","coding","reading",
            "concentrate","productivity","deep work"
        ],

        "calm": [
            "calm","relax","peaceful","meditate","chill","quiet",
            "sleep","rest","slow"
        ]
    }

    scores = {mood:0 for mood in mood_keywords}

    for mood, keywords in mood_keywords.items():
        for word in keywords:
            if word in text:
                scores[mood] += 1

    detected_mood = max(scores, key=scores.get)

    if scores[detected_mood] == 0:
        return None

    return detected_mood
 
song_db = {

"happy":[
{"title":"Ilahi","artist":"Arijit Singh"},
{"title":"Gallan Goodiyan","artist":"Yashita Sharma"},
{"title":"Kar Gayi Chull","artist":"Badshah"},
{"title":"Happy","artist":"Pharrell Williams"},
{"title":"On Top of the World","artist":"Imagine Dragons"}
],

"sad":[
{"title":"Channa Mereya","artist":"Arijit Singh"},
{"title":"Agar Tum Saath Ho","artist":"Alka Yagnik, Arijit Singh"},
{"title":"Tujhe Bhula Diya","artist":"Mohit Chauhan"},
{"title":"Someone Like You","artist":"Adele"},
{"title":"Fix You","artist":"Coldplay"}
],

"romantic":[
{"title":"Kesariya","artist":"Arijit Singh"},
{"title":"Tum Hi Ho","artist":"Arijit Singh"},
{"title":"Raabta","artist":"Arijit Singh"},
{"title":"Perfect","artist":"Ed Sheeran"},
{"title":"All of Me","artist":"John Legend"}
],

"energetic":[
{"title":"Malhari","artist":"Vishal Dadlani"},
{"title":"Zinda","artist":"Siddharth Mahadevan"},
{"title":"Jai Jai Shivshankar","artist":"Vishal & Shekhar"},
{"title":"Believer","artist":"Imagine Dragons"},
{"title":"Eye of the Tiger","artist":"Survivor"}
],

"focus":[
{"title":"Kun Faya Kun","artist":"A.R. Rahman"},
{"title":"Phir Le Aaya Dil","artist":"Arijit Singh"},
{"title":"Agar Tum Saath Ho (Instrumental)","artist":"A.R. Rahman"},
{"title":"Clair de Lune","artist":"Claude Debussy"},
{"title":"Experience","artist":"Ludovico Einaudi"}
],

"calm":[
{"title":"Iktara","artist":"Amit Trivedi"},
{"title":"Kabira (Encore)","artist":"Arijit Singh"},
{"title":"Shayad","artist":"Arijit Singh"},
{"title":"Weightless","artist":"Marconi Union"},
{"title":"River Flows In You","artist":"Yiruma"}
]

}

mood_query = {
    "happy": "happy",
    "sad": "sad",
    "romantic": "love",
    "energetic": "workout",
    "focus": "lofi",
    "calm": "instrumental"
}

def get_spotify_songs(query):

    print("Query sent to Spotify:", query)

    try:
        results = sp.search(q=query, limit=5, type='track', market='IN')
        print("Spotify response:", results)
    except Exception as e:
        print("Spotify API error:", e)
        return []

    tracks = results.get("tracks", {}).get("items", [])
    print("Tracks found:", len(tracks))

    songs = []

    for track in tracks:
        songs.append({
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "image": track['album']['images'][0]['url'],
            "link": track['external_urls']['spotify'],
            "preview": track['preview_url'] or ""
        })
    return songs



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message", "")

    try:

        mood = detect_mood(user_message)

        if not mood:
            mood = "calm"

        query = mood_query[mood]

        songs = get_spotify_songs(query)
        if not songs:
            songs = song_db.get(mood, [])

        return jsonify({
            "mood": mood,
            "songs": songs
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)})
    
if __name__ == "__main__":
    app.run(debug=True)