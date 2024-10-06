# from django.contrib import admin

# # Register your models here.

# from .models import Movie


# class MovieAdmin(admin.ModelAdmin):
#     fields = ['imdb_id', 'genres', 'original_title', 'overview', 'watched']
#     list_display = ('original_title', 'genres', 'release_date', 'watched')
#     search_fields = ['original_title', 'overview']


# admin.site.register(Movie, MovieAdmin)

from django.contrib import admin
from .models import Movie, UserMovie

class MovieAdmin(admin.ModelAdmin):
    fields = ['imdb_id', 'genres', 'original_title', 'overview']
    list_display = ('original_title', 'genres', 'release_date')
    search_fields = ['original_title', 'overview']

class UserMovieAdmin(admin.ModelAdmin):
    fields = ['user', 'movie', 'watched', 'recommended', 'rating']
    list_display = ('user', 'movie', 'watched', 'recommended', 'rating')
    list_filter = ('user', 'watched', 'recommended')
    search_fields = ['user__username', 'movie__original_title']

admin.site.register(Movie, MovieAdmin)
admin.site.register(UserMovie, UserMovieAdmin)