from recommendations.models import Song, Movie
from .spotify_client import fetch_spotify_songs
from .tmdb_client import fetch_tmdb_movies

def hybrid_recommend(mood):
    results = {
        "mood": mood,
        "songs": [],
        "movies": [],
        "sources": {}
    }
    
    # Try Spotify API
    try:
        spotify_songs = fetch_spotify_songs(mood)
        if spotify_songs:
            results["songs"] = spotify_songs
            results["sources"]["songs"] = "Spotify API"
    except Exception as e:
        print(f"Spotify API Error: {str(e)}")
    
    # Try TMDB API
    try:
        tmdb_movies = fetch_tmdb_movies(mood)
        if tmdb_movies:
            results["movies"] = tmdb_movies
            results["sources"]["movies"] = "TMDB API"
    except Exception as e:
        print(f"TMDB API Error: {str(e)}")
    
    # Fallback to local database
    if not results["songs"]:
        results["songs"] = list(Song.objects.filter(mood__icontains=mood).values('title', 'artist')[:5])
        results["sources"]["songs"] = "Local Database"
    
    if not results["movies"]:
        results["movies"] = list(Movie.objects.filter(mood__icontains=mood).values('title', 'genre')[:5])
        results["sources"]["movies"] = "Local Database"
    
    return results