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
        # 只有在 POST 时才提交评分和训练模型
        for movie_id, score in request.POST.items():
            if movie_id.startswith("movie_") and score:
                mid = int(movie_id.replace("movie_", ""))
                Rating.objects.create(user=request.user, movie_id=mid, score=float(score))

        print("✅ 已提交评分，调用推荐模型")
        generate_itemcf_for_user_mysql(request.user.id)
        return redirect("show_recommendation")

    # GET 请求：仅展示打分页，绝不调用训练函数
    print("📄 进入评分页面 GET 请求，无推荐逻辑")
    movies = Movie.objects.order_by("?")[:10]

    for m in movies:
        main_genre = m.genres.split("|")[0] if m.genres else "default"
        m.poster_url = f"posters/{main_genre.strip()}.png"
        m.tag_list = [t.strip() for t in m.tags.split("|") if t.strip()] if isinstance(m.tags, str) else []

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


from django.template.loader import render_to_string

@require_POST
def replace_rating(request, movie_id):
    # ✅ 移除当前电影 ID，准备候选列表
    existing_ids = list(Movie.objects.all().values_list('movie_id', flat=True))
    if movie_id in existing_ids:
        existing_ids.remove(movie_id)

    candidates = Movie.objects.exclude(movie_id__in=[movie_id])
    if not candidates.exists():
        return JsonResponse({'success': False, 'message': '没有可替换的电影'})

    new_movie = random.choice(list(candidates))

    # ✅ 添加 poster_url 和 tag_list（重要）
    main_genre = new_movie.genres.split("|")[0] if new_movie.genres else "default"
    new_movie.poster_url = f'posters/{main_genre.strip()}.png'
    new_movie.tag_list = [t.strip() for t in new_movie.tags.split("|") if t.strip()] if isinstance(new_movie.tags, str) else []

    # ✅ 渲染组件模板
    html = render_to_string('components/movie_card.html', {
        'movie': new_movie
    }, request=request)

    return JsonResponse({
        'success': True,
        'html': html
    })

