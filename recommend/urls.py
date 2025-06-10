from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('rate/', views.rate_movies, name='rate_movies'),
    path('recommend/', views.show_recommendations, name='show_recommendation'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
]