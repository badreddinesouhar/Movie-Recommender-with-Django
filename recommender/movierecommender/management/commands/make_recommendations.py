# from django.core.management import BaseCommand
# from ...models import Movie


# # Check if genres are valid
# def check_valid_genres(genres: str) -> bool:
#     if bool(genres and not genres.isspace()) and genres != 'na':
#         return True
#     else:
#         return False

# # Add a Jaccard similarity method here

# # Add a movie similarity method here


# class Command(BaseCommand):
#     help = 'Recommend movies'

#     def add_arguments(self, parser):
#         pass

#     def handle(self, *args, **kwargs):
#         # Figure the recommended field for each unwatched movie
#         # Based on the similarity on movie genres
#         pass

# # Method to calculate Jaccard Similarity
# def jaccard_similarity(list1: list, list2: list) -> float:
#     s1 = set(list1)
#     s2 = set(list2)
#     return float(len(s1.intersection(s2)) / len(s1.union(s2)))

# # Calculate the similarity between two movies
# def similarity_between_movies(movie1: Movie, movie2: Movie) -> float:
#     if check_valid_genres(movie1.genres) and check_valid_genres(movie2.genres):
#         m1_generes = movie1.genres.split()
#         m2_generes = movie2.genres.split()
#         return jaccard_similarity(m1_generes, m2_generes)
#     else:
#         return 0

# # python manage.py make_recommendations

from django.core.management import BaseCommand
from ...models import Movie
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime

def check_valid_field(field):
    if isinstance(field, str):
        return bool(field and not field.isspace() and field.lower() != 'na')
    elif isinstance(field, (int, float)):
        return True  # Assuming any number is valid
    else:
        return bool(field)  # For other types, just check if it's truthy

def preprocess_text(text: str) -> str:
    # Simple preprocessing: lowercase and remove extra spaces
    return ' '.join(text.lower().split())

def calculate_similarity(movie1: Movie, movie2: Movie) -> float:
    similarity = 0.0
    weight_sum = 0.0

    # Genre similarity
    if check_valid_field(movie1.genres) and check_valid_field(movie2.genres):
        genre_sim = jaccard_similarity(movie1.genres.split(), movie2.genres.split())
        similarity += 0.4 * genre_sim
        weight_sum += 0.4

    # Language similarity
    if check_valid_field(movie1.original_language) and check_valid_field(movie2.original_language):
        lang_sim = 1.0 if movie1.original_language == movie2.original_language else 0.0
        similarity += 0.2 * lang_sim
        weight_sum += 0.2

    # Release year similarity
    if check_valid_field(movie1.release_date) and check_valid_field(movie2.release_date):
        year1 = movie1.release_date.year if isinstance(movie1.release_date, datetime) else int(str(movie1.release_date).split(',')[-1])
        year2 = movie2.release_date.year if isinstance(movie2.release_date, datetime) else int(str(movie2.release_date).split(',')[-1])
        year_diff = abs(year1 - year2)
        year_sim = max(0, 1 - (year_diff / 10))  # Assume 10 years difference is maximum
        similarity += 0.2 * year_sim
        weight_sum += 0.2

    # Vote average similarity
    if movie1.vote_average is not None and movie2.vote_average is not None:
        vote_diff = abs(float(movie1.vote_average) - float(movie2.vote_average))
        vote_sim = max(0, 1 - (vote_diff / 10))
        similarity += 0.2 * vote_sim
        weight_sum += 0.2

    return similarity / weight_sum if weight_sum > 0 else 0.0

def jaccard_similarity(list1: list, list2: list) -> float:
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))

class Command(BaseCommand):
    help = 'Recommend movies'

    def add_arguments(self, parser):
        parser.add_argument('movie_id', type=int, help='ID of the movie to get recommendations for')
        parser.add_argument('--top', type=int, default=5, help='Number of top recommendations to return')

    def handle(self, *args, **kwargs):
        movie_id = kwargs['movie_id']
        top_n = kwargs['top']

        try:
            target_movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Movie with ID {movie_id} does not exist'))
            return

        all_movies = Movie.objects.exclude(id=movie_id)
        similarities = [(movie, calculate_similarity(target_movie, movie)) for movie in all_movies]
        similarities.sort(key=lambda x: x[1], reverse=True)

        self.stdout.write(self.style.SUCCESS(f'Top {top_n} recommendations for "{target_movie.original_title}":'))
        for movie, similarity in similarities[:top_n]:
            self.stdout.write(f'- {movie.original_title} (Similarity: {similarity:.2f})')

# Usage: python manage.py make_recommendations <movie_id> --top <number_of_recommendations>