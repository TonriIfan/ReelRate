from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Movie, Rating, RecommendedMovie

# 先注销默认 User 注册
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('movie_id', 'title')
    search_fields = ('title',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score')
    search_fields = ('user__username', 'movie__title')

@admin.register(RecommendedMovie)
class RecommendedMovieAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score')
    search_fields = ('user__username', 'movie__title')
