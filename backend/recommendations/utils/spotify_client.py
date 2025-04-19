import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings

def get_spotify_client():
    return spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET
        )
    )

def fetch_spotify_songs(mood, limit=5):
    try:
        sp = get_spotify_client()
        mood_query_map = {
            "joy": "happy bollywood",
            "sadness": "sad bollywood",
            "anger": "energetic punjabi",
            "love": "romantic bollywood"
        }
        
        results = sp.search(
            q=mood_query_map.get(mood, "bollywood"),
            limit=limit,
            type="track",
            market="IN"
        )
        
        return [{
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "spotify_id": track['id']
        } for track in results['tracks']['items']]
    
    except Exception as e:
        print(f"Spotify Error: {str(e)}")
        return []