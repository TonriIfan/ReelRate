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
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from recommend.models import RecommendedMovie, Movie
import random

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

    for rec in recommended:
        genres = rec.movie.genres
        main_genre = genres.split("|")[0] if genres else "default"
        rec.poster_url = f'posters/{main_genre}.png'

    return render(request, "recommend.html", {"recommended_movies": recommended})





def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # ✅ 检查用户是否存在
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "用户不存在，请先注册")
            return render(request, "login.html")

        # ✅ 尝试认证用户（密码是否正确）
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "该账号已被禁用，请联系管理员")
            else:
                login(request, user)
                return redirect("rate_movies")
        else:
            messages.error(request, "密码错误，请重试")

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
        # 提取主类型
        main_genre = m.genres.split("|")[0] if m.genres else "default"
        m.poster_url = f"posters/{main_genre.strip()}.png" # 所有图片都是我用ai生成的
        # 分割标签
        if isinstance(m.tags, str):
            m.tag_list = [t.strip() for t in m.tags.split("|") if t.strip()]
        else:
            m.tag_list = []

    print("用户评分记录：", Rating.objects.filter(user=request.user).count())

    return render(request, "rate.html", {"movies": movies})

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "用户名已存在")
        elif password1 != password2:
            messages.error(request, "两次密码输入不一致")
        else:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            return redirect("rate_movies")

    return render(request, "register.html")


@require_POST
def replace_movie(request, rec_id):
    try:
        rec = RecommendedMovie.objects.get(id=rec_id, user=request.user)
    except RecommendedMovie.DoesNotExist:
        return JsonResponse({'success': False, 'message': '推荐不存在'})

    rated_movie_ids = list(RecommendedMovie.objects.filter(user=request.user).values_list('movie_id', flat=True))
    new_candidates = Movie.objects.exclude(movie_id__in=rated_movie_ids)

    if not new_candidates.exists():
        return JsonResponse({'success': False, 'message': '无可替换电影'})

    new_movie = random.choice(list(new_candidates))
    rec.movie = new_movie
    rec.score = random.uniform(3.5, 5.0)  # 可以替换为算法推荐分数
    rec.save()

    main_genre = new_movie.genres.split("|")[0] if new_movie.genres else "default"
    poster_url = f'posters/{main_genre}.png'

    return JsonResponse({
        'success': True,
        'title': new_movie.title,
        'genres': new_movie.genres,
        'score': rec.score,
        'poster_url': poster_url
    })