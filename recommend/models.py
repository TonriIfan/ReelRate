from django.db import models


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"User {self.user_id}"


class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    genres = models.CharField(max_length=200, blank=True)  # 添加这行
    tags = models.TextField(blank=True)  # 添加这行

    def __str__(self):
        return self.title


from django.contrib.auth.models import User


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return f"{self.user} rated {self.movie} with {self.score}"


class RecommendedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return f"Recommended: {self.movie} to {self.user} (score: {self.score})"
