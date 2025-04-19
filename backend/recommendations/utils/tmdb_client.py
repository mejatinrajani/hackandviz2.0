import requests
from django.conf import settings

def fetch_tmdb_movies(mood, limit=5):
    try:
        genre_map = {
            "joy": 35,     # Comedy
            "sadness": 18, # Drama
            "love": 10749, # Romance
            "anger": 28     # Action
        }
        
        response = requests.get(
            "https://api.themoviedb.org/3/discover/movie",
            params={
                "api_key": settings.TMDB_API_KEY,
                "with_genres": genre_map.get(mood, 35),
                "with_original_language": "hi",
                "region": "IN",
                "sort_by": "popularity.desc"
            }
        ).json()
        
        return [{
            "title": movie['title'],
            "year": movie['release_date'][:4] if movie.get('release_date') else "N/A",
            "genre": get_genre_name(movie['genre_ids'][0] if movie['genre_ids'] else None)
        } for movie in response.get('results', [])[:limit]]
    
    except Exception as e:
        print(f"TMDB Error: {str(e)}")
        return []

def get_genre_name(genre_id):
    genres = {
        35: "Comedy",
        18: "Drama",
        10749: "Romance",
        28: "Action"
    }
    return genres.get(genre_id, "Unknown")