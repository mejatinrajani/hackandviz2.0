from django.core.management.base import BaseCommand
from recommendations.models import Song, Movie

class Command(BaseCommand):
    help = 'Seed initial Indian content'
    
    def handle(self, *args, **kwargs):
        # Bollywood Songs
        Song.objects.create(
            title="Tum Hi Ho",
            artist="Arijit Singh",
            features={"valence": 0.92, "energy": 0.75, "tempo": 110},
            mood="romantic",
            language="Hindi"
        )
        
        # Indian Movies
        Movie.objects.create(
            title="Jab We Met",
            genre="Romance",
            keywords="train journey, love story, comedy",
            mood="romantic",
            language="Hindi"
        )
        self.stdout.write("Successfully seeded Indian content!")