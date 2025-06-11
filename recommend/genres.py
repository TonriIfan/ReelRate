import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ReelRate.settings")
django.setup()
from recommend.models import Movie

BASE_DIR = Path(__file__).resolve().parent.parent  # 项目根目录

def extract_unique_genres():
    genre_set = set()

    for movie in Movie.objects.all().only('genres'):
        if movie.genres:
            parts = movie.genres.split("|")
            genre_set.update(g.strip() for g in parts if g.strip())

    genres_sorted = sorted(genre_set)

    # ✅ 使用 BASE_DIR 拼接 artifacts/genres.txt
    output_path = BASE_DIR / "artifacts" / "genres.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)  # 自动创建目录
    with open(output_path, "w", encoding="utf-8") as f:
        for g in genres_sorted:
            f.write(g + "\n")

    return genres_sorted


if __name__ == "__main__":
    genres = extract_unique_genres()
    print("🎬 共发现类型：", len(genres))
    for g in genres:
        print("-", g)
