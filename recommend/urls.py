from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 👈 首页 URL
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('rate/', views.rate_movies, name='rate_movies'),
    path('recommend/', views.show_recommendations, name='show_recommendation'),
]