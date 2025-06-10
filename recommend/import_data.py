import csv
from tqdm import tqdm
from recommend.models import User, Movie, Rating
from django.db import transaction

BATCH_SIZE = 10000

def import_ratings_from_csv(csv_path='ratings_with_tags.csv'):
    print(f"📥 开始导入评分数据：{csv_path}")

    user_cache = {}
    movie_cache = {}
    rating_batch = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0

        for row in reader:
            user_id = int(row['user_id'])
            movie_id = int(row['movie_id'])
            title = row['title']
            genres = row.get('genres', '') or ''
            tags = row.get('tags', '') or ''
            score = float(row['score'])

            # 缓存用户
            if user_id not in user_cache:
                user, _ = User.objects.get_or_create(user_id=user_id)
                user_cache[user_id] = user
            user = user_cache[user_id]

            # 缓存电影
            if movie_id not in movie_cache:
                movie, _ = Movie.objects.get_or_create(
                    movie_id=movie_id,
                    defaults={'title': title, 'genres': genres, 'tags': tags}
                )
                movie_cache[movie_id] = movie
            movie = movie_cache[movie_id]

            rating_batch.append(Rating(user=user, movie=movie, score=score))
            count += 1

            # 批量写入
            if len(rating_batch) >= BATCH_SIZE:
                Rating.objects.bulk_create(rating_batch)
                print(f"✅ 已导入 {count} 条评分...")
                rating_batch.clear()

        # 最后一批
        if rating_batch:
            Rating.objects.bulk_create(rating_batch)
            print(f"✅ 最后批次写入完成，总数 {count} 条评分")

    print("🎉 数据导入完成！")
