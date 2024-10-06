# from django.db import models


# # Create your models here.
# # HINT: Create a Movie model here
# # It will be mapped to a database table with columns
# class Movie(models.Model):
#     """
#     Django Movie Model
#     """
#     # IMDB id
#     imdb_id = models.CharField(max_length=48, null=False)
#     # Movie genres
#     genres = models.CharField(max_length=200, null=True)
#     # Original language
#     original_language = models.CharField(max_length=20, null=True)
#     # Original movie title
#     original_title = models.CharField(max_length=500, null=False)
#     # Movie release date
#     release_date = models.IntegerField(default=1970)
#     # Movie overview
#     overview = models.TextField(max_length=2000, null=True)
#     # Average voting for the movie
#     vote_average = models.FloatField(default=0)
#     # Total votes for ths movie
#     vote_count = models.IntegerField(default=0)
#     # The movie's poster path
#     poster_path = models.CharField(max_length=64, null=True)
#     # If you have watched this movie
#     watched = models.BooleanField(default=False, null=True)
#     # If this movie will be recommended
#     recommended = models.BooleanField(default=False, null=True)

# models.py
from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    imdb_id = models.CharField(max_length=48, null=False)
    genres = models.CharField(max_length=200, null=True)
    original_language = models.CharField(max_length=20, null=True)
    original_title = models.CharField(max_length=500, null=False)
    release_date = models.IntegerField(default=1970)
    overview = models.TextField(max_length=2000, null=True)
    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    poster_path = models.CharField(max_length=64, null=True)

class UserMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)
    recommended = models.BooleanField(default=False)
    rating = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'movie')