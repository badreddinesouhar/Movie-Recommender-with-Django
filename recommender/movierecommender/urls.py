from django.urls import path
from . import views
from .views import SignUpView

urlpatterns = [
    path('', views.home, name='home'),
    path('recommendations/', views.movie_recommendation_view, name='movie_recommendation_view'),
    path('user_recommendations/', views.recommendations, name='user_recommendations'),
    path('mark_watched/<int:movie_id>/', views.mark_as_watched, name='mark_as_watched'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('movies/', views.movie_list, name='movie_list'),
]
