import csv
import pandas as pd
# from django.core.management import BaseCommand
# from ...models import Movie

# class Command(BaseCommand):
#     help = 'Load a movie csv file into the database'

#     def add_arguments(self, parser):
#         parser.add_argument('--path', type=str)
    
#     def handle(self, *args, **kwargs):
#     THRESHOLD = 0.8
#     # Get all watched and unwatched movies
#     watched_movies = Movie.objects.filter(
#             watched=True)
#     unwatched_movies = Movie.objects.filter(
#             watched=False)
#     # Start to generate recommendations in unwatched movies
#     for unwatched_movie in unwatched_movies:
#         max_similarity = 0
#         will_recommend = False
#         # For each watched movie
#         for watched_movie in watched_movies:
#             # Calculate the similarity between watched_movie and all unwatched movies
#             similarity = similarity_between_movies(unwatched_movie, watched_movie)
#             if similarity >= max_similarity:
#                 max_similarity = similarity
#             # early stop if the unwatched_movie is similar enough
#             if max_similarity >= THRESHOLD:
#                 break
#         # If unwatched_movie is similar enough to watched movies
#         # Then recommend it
#         if max_similarity > THRESHOLD:
#             will_recommend = True
#             print(f"Find a movie recommendation: {unwatched_movie.original_title}")

#         unwatched_movie.recommended = will_recommend
#         unwatched_movie.save()


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movierecommender.models import Movie, UserMovie

class Command(BaseCommand):
    help = 'Generate movie recommendations for users'

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, help='ID of the user to generate recommendations for')

    def handle(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        THRESHOLD = 0.8

        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            users = User.objects.all()

        for user in users:
            self.stdout.write(f"Generating recommendations for user: {user.username}")
            watched_movies = UserMovie.objects.filter(user=user, watched=True)
            unwatched_movies = UserMovie.objects.filter(user=user, watched=False)

            for unwatched_user_movie in unwatched_movies:
                max_similarity = 0
                will_recommend = False

                for watched_user_movie in watched_movies:
                    similarity = similarity_between_movies(unwatched_user_movie.movie, watched_user_movie.movie)
                    if similarity > max_similarity:
                        max_similarity = similarity
                    if max_similarity >= THRESHOLD:
                        break

                if max_similarity > THRESHOLD:
                    will_recommend = True
                    self.stdout.write(f"Recommending {unwatched_user_movie.movie.original_title} to {user.username}")

                unwatched_user_movie.recommended = will_recommend
                unwatched_user_movie.save()

def similarity_between_movies(movie1, movie2):
    # Implement your similarity calculation logic here
    # This is a placeholder function
    return 0.5

    # def handle(self, *args, **kwargs):
    #     # Remove any existing data
    #     print("Clean old movie data")
    #     Movie.objects.all().delete()
    #     path = kwargs['path']
    #     # Read the movie csv file as a dataframe
    #     movie_df = pd.read_csv(path)
    #     # Iterate each row in the dataframe
    #     for index, row in movie_df.iterrows():
    #         imdb_id = row["imdb_id"]
    #         genres = row["genres"]
    #         release_date = row["release_date"]
    #         original_language = row["original_language"]
    #         original_title = row["original_title"]
    #         overview = row["overview"]
    #         vote_average = row["vote_average"]
    #         vote_count = row["vote_count"]
    #         poster_path = row["poster_path"]
    #         # Populate Movie object for each row
    #         movie = Movie(imdb_id=imdb_id,
    #                         genres=genres,
    #                         original_title=original_title,
    #                         original_language=original_language,
    #                         release_date=release_date,
    #                         overview=overview,
    #                         vote_average=vote_average,
    #                         vote_count=vote_count,
    #                         poster_path=poster_path)
    #         # Save movie object
    #         movie.save()
    #         print(f"Movie: {imdb_id}, {original_title} saved...")

# python manage.py load_movies --path movies.csv