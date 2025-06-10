from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from recommend.models import Rating, Movie, RecommendedMovie
# from recommend.recommender.train_itemcf_simple import generate_itemcf_for_user
# from recommend.recommender.train_itemcf_spark import generate_itemcf_for_user_spark
from recommend.recommender.train_itemcf_mysql import generate_itemcf_for_user_mysql
from recommend.export.export_ratings_csv import export_ratings_csv

def index(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "用户名已存在")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)  # 自动登录
            return redirect("rate_movies")  # 注册后跳转打分页
    return render(request, "register.html")


# @login_required
# def rate_movies(request):
#     if request.method == "POST":
#         # 提交评分
#         for movie_id, score in request.POST.items():
#             if movie_id.startswith("movie_") and score:
#                 mid = int(movie_id.replace("movie_", ""))
#                 Rating.objects.create(user=request.user, movie_id=mid, score=float(score))
#
#         # 自动生成个性化推荐
#         generate_itemcf_for_user(request.user.id)
#
#         return redirect("show_recommendation")
#
#     # 否则随机取 10 部电影打分
#     movies = Movie.objects.order_by("?")[:10]
#     return render(request, "rate.html", {"movies": movies})
# @login_required
# def rate_movies(request):
#     if request.method == "POST":
#         for movie_id, score in request.POST.items():
#             if movie_id.startswith("movie_") and score:
#                 mid = int(movie_id.replace("movie_", ""))
#                 Rating.objects.create(user=request.user, movie_id=mid, score=float(score))
#
#         # ✅ 导出评分 CSV 文件
#         export_ratings_csv("ratings.csv")
#
#         # ✅ 使用 PySpark 推荐逻辑
#         generate_itemcf_for_user_spark("ratings.csv", request.user.id)
#
#         return redirect("show_recommendation")
#
#     # ✅ 处理 GET 请求时展示打分页
#     movies = Movie.objects.order_by("?")[:10]
#     return render(request, "rate.html", {"movies": movies})
@login_required
def rate_movies(request):
    if request.method == "POST":
        for movie_id, score in request.POST.items():
            if movie_id.startswith("movie_") and score:
                mid = int(movie_id.replace("movie_", ""))
                Rating.objects.create(user=request.user, movie_id=mid, score=float(score))

        # ✅ 直接从 MySQL 使用 Spark 生成推荐（不需要 CSV）
        generate_itemcf_for_user_mysql(request.user.id)

        return redirect("show_recommendation")

    # ✅ 处理 GET 请求时展示打分页
    movies = Movie.objects.order_by("?")[:10]
    return render(request, "rate.html", {"movies": movies})


@login_required
def show_recommendations(request):
    recommended = RecommendedMovie.objects.filter(user=request.user).select_related('movie')
    return render(request, "recommend.html", {"recommended_movies": recommended})



def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("rate_movies")
        else:
            messages.error(request, "用户名或密码错误")
    return render(request, "login.html")


@login_required
def rate_movies(request):
    if request.method == "POST":
        for movie_id, score in request.POST.items():
            if movie_id.startswith("movie_") and score:
                mid = int(movie_id.replace("movie_", ""))
                Rating.objects.create(user=request.user, movie_id=mid, score=float(score))

        generate_itemcf_for_user_mysql(request.user.id)
        return redirect("show_recommendation")

    movies = Movie.objects.order_by("?")[:10]

    # ✅ 给每部电影添加 tags 列表字段（预处理）
    for m in movies:
        if isinstance(m.tags, str):
            m.tag_list = [t.strip() for t in m.tags.split("|") if t.strip()]
        else:
            m.tag_list = []

    return render(request, "rate.html", {"movies": movies})
