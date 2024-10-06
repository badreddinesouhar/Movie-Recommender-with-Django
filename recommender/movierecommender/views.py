# from . import views
# from .models import Movie
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import UserMovie

# # HINT: Create a view to provide movie recommendations list for the HTML template

# def movie_recommendation_view(request):
#     if request.method == "GET":
#       # The context/data to be presented in the HTML template
#       context = generate_movies_context()
#       # Render a HTML page with specified template and context
#       return render(request, 'movierecommender/movie_list.html', context)

# def generate_movies_context():
#     context = {}
#     # Show only movies in recommendation list
#     # Sorted by vote_average in desc
#     # Get recommended movie counts
#     recommended_count = Movie.objects.filter(
#         recommended=True
#     ).count()
#     # If there are no recommended movies
#     if recommended_count == 0:
#         # Just return the top voted and unwatched movies as popular ones
#         movies = Movie.objects.filter(
#             watched=False
#         ).order_by('-vote_count')[:30]
#     else:
#         # Get the top voted, unwatched, and recommended movies
#         movies = Movie.objects.filter(
#             watched=False
#         ).filter(
#             recommended=True
#         ).order_by('-vote_count')[:30]
#     context['movie_list'] = movies
#     return context

# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Movie, UserMovie

# def home(request):
#     return render(request, 'movierecommender/home.html')

# @login_required
# def movie_recommendation_view(request):
#     if request.method == "GET":
#         context = generate_movies_context(request.user)
#         return render(request, 'movierecommender/movie_list.html', context)

# def generate_movies_context(user):
#     context = {}
#     # Get recommended movies for the user
#     recommended_movies = UserMovie.objects.filter(
#         user=user,
#         recommended=True,
#         watched=False
#     ).select_related('movie').order_by('-movie__vote_count')[:30]
    
#     # If there are no recommended movies
#     if not recommended_movies:
#         # Get unwatched movies for the user
#         unwatched_movies = UserMovie.objects.filter(
#             user=user,
#             watched=False
#         ).select_related('movie').order_by('-movie__vote_count')[:30]
#         context['movie_list'] = [um.movie for um in unwatched_movies]
#     else:
#         context['movie_list'] = [rm.movie for rm in recommended_movies]
    
#     return context

# @login_required
# def recommendations(request):
#     user_movies = UserMovie.objects.filter(
#         user=request.user, 
#         recommended=True, 
#         watched=False
#     ).select_related('movie')
#     return render(request, 'movierecommender/recommendations.html', {'user_movies': user_movies})

# @login_required
# def mark_as_watched(request, movie_id):
#     if request.method == "POST":
#         user_movie, created = UserMovie.objects.get_or_create(
#             user=request.user,
#             movie_id=movie_id
#         )
#         user_movie.watched = True
#         user_movie.save()
#         # You might want to add a success message here
#     return redirect('movie_recommendation_view')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from .models import Movie, UserMovie
from collections import Counter
import datetime


def home(request):
    return render(request, 'movierecommender/home.html')



# @login_required
# def movie_recommendation_view(request):
#     # Your existing code for fetching recommendations
#     context = generate_movies_context(request.user)
#     return render(request, 'movierecommender/movie_list.html', context)

def generate_movies_context(user):
    context = {}
    # Get recommended movies for the user
    recommended_movies = UserMovie.objects.filter(
        user=user,
        recommended=True,
        watched=False
    ).select_related('movie').order_by('-movie__vote_count')[:30]
    
    # If there are no recommended movies
    if not recommended_movies:
        # Get unwatched movies for the user
        unwatched_movies = UserMovie.objects.filter(
            user=user,
            watched=False
        ).select_related('movie').order_by('-movie__vote_count')[:30]
        context['movie_list'] = [um.movie for um in unwatched_movies]
    else:
        context['movie_list'] = [rm.movie for rm in recommended_movies]
    
    return context


@login_required
def recommendations(request):
    user_movies = UserMovie.objects.filter(user=request.user, recommended=True)
    return render(request, 'movierecommender/recommendations.html', {'user_movies': user_movies})

@login_required
def mark_as_watched(request, movie_id):
    if request.method == "POST":
        user_movie, created = UserMovie.objects.get_or_create(
            user=request.user,
            movie_id=movie_id
        )
        user_movie.watched = True
        user_movie.save()
    return redirect('movie_recommendation_view')

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def movie_list(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        if movie_id:
            movie = Movie.objects.get(id=movie_id)
            UserMovie.objects.get_or_create(user=request.user, movie=movie, watched=True)
        return redirect('movie_list')
    
    movies = Movie.objects.all()
    watched_movies = UserMovie.objects.filter(user=request.user, watched=True).values_list('movie_id', flat=True)
    context = {
        'movies': movies,
        'watched_movies': watched_movies,
    }
    return render(request, 'movierecommender/movie_list.html', context)

@login_required
def movie_recommendation_view(request):
    # Get the user's watched movies
    watched_movies = UserMovie.objects.filter(user=request.user, watched=True).select_related('movie')
    
    if not watched_movies:
        # If the user hasn't watched any movies, recommend top-rated movies
        recommended_movies = Movie.objects.order_by('-vote_average')[:10]
    else:
        # Analyze user's preferences
        genre_preference = Counter()
        avg_release_year = 0
        avg_vote = 0
        
        for user_movie in watched_movies:
            movie = user_movie.movie
            genres = movie.genres.split(',')
            genre_preference.update(genres)
            avg_release_year += int(movie.release_date[:4])  # Assuming release_date is in 'YYYY-MM-DD' format
            avg_vote += movie.vote_average
        
        avg_release_year //= len(watched_movies)
        avg_vote /= len(watched_movies)
        
        # Get top 3 preferred genres
        top_genres = [genre for genre, _ in genre_preference.most_common(3)]
        
        # Build query for recommendations
        recommendation_query = Q()
        for genre in top_genres:
            recommendation_query |= Q(genres__icontains=genre)
        
        # Exclude watched movies and filter by preferred genres
        potential_recommendations = Movie.objects.exclude(
            id__in=watched_movies.values_list('movie_id', flat=True)
        ).filter(recommendation_query)
        
        # Score movies based on genre match, release year proximity, and vote average
        scored_movies = []
        current_year = datetime.datetime.now().year
        for movie in potential_recommendations:
            score = 0
            # Genre match score
            movie_genres = set(movie.genres.split(','))
            score += len(movie_genres.intersection(top_genres)) * 2
            
            # Release year proximity score
            year_diff = abs(int(movie.release_date[:4]) - avg_release_year)
            score += max(0, 5 - year_diff * 0.5)  # Max 5 points, decreasing by 0.5 for each year difference
            
            # Vote average score
            if movie.vote_average >= avg_vote:
                score += min(5, (movie.vote_average - avg_vote) * 2)  # Max 5 points
            
            scored_movies.append((movie, score))
        
        # Sort movies by score and get top 10
        recommended_movies = [movie for movie, score in sorted(scored_movies, key=lambda x: x[1], reverse=True)[:10]]
    
    context = {
        'recommended_movies': recommended_movies,
        'watched_count': len(watched_movies) if watched_movies else 0
    }
    return render(request, 'movierecommender/recommendations.html', context)

# Make sure to implement the generate_movies_context function