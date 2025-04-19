from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    features = models.JSONField()  # {"valence": 0.95, "energy": 0.8, "tempo": 120}
    mood = models.CharField(max_length=50)  # happy/sad/romantic/energetic
    language = models.CharField(max_length=20)  # Hindi/English/Tamil

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    keywords = models.TextField()  # Comma-separated tags
    mood = models.CharField(max_length=50)
    language = models.CharField(max_length=20)