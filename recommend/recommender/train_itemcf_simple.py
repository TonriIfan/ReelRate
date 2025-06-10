# # recommend/recommender/train_itemcf_simple.py
#
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
# from recommend.models import Rating, RecommendedMovie, Movie, User
# from django.db import transaction
#
# def generate_itemcf_for_user(user_id: int, top_n: int = 10):
#     # Step 1: 获取所有评分数据
#     ratings = Rating.objects.all().values("user__id", "movie__movie_id", "score")
#     print(f"🎯 为用户 {user_id} 生成个性化推荐")
#     df = pd.DataFrame(ratings)
#
#     if df[df["user__id"] == user_id].empty:
#         print(f"⚠ 用户 {user_id} 没有评分，跳过推荐")
#         return
#
#     df.columns = ["user_id", "movie_id", "score"]
#
#     # Step 2: 构建用户-物品评分矩阵（行是 item，列是 user）
#     matrix = df.pivot_table(index="movie_id", columns="user_id", values="score").fillna(0)
#
#     # Step 3: 计算物品相似度矩阵
#     similarity_matrix = pd.DataFrame(
#         cosine_similarity(matrix),
#         index=matrix.index,
#         columns=matrix.index
#     )
#
#     # Step 4: 获取当前用户看过的电影
#     user_rated = df[df["user_id"] == user_id].set_index("movie_id")["score"]
#     seen_movies = set(user_rated.index)
#
#     # Step 5: 基于相似度加权计算推荐得分
#     scores = {}
#     for seen_id, rating in user_rated.items():
#         similar_items = similarity_matrix[seen_id].drop(index=seen_movies)
#         for target_id, sim in similar_items.items():
#             if target_id not in scores:
#                 scores[target_id] = 0
#             scores[target_id] += rating * sim
#
#     # Step 6: 排序并获取 Top N
#     ranked_movies = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
#
#     # Step 7: 保存推荐结果
#     user = User.objects.get(id=user_id)
#     RecommendedMovie.objects.filter(user=user).delete()
#
#     batch = []
#     for mid, score in ranked_movies:
#         try:
#             movie = Movie.objects.get(movie_id=mid)
#             batch.append(RecommendedMovie(user=user, movie=movie, score=score))
#         except Movie.DoesNotExist:
#             print(f"❗Movie ID {mid} 不存在，跳过")
#
#     with transaction.atomic():
#         RecommendedMovie.objects.bulk_create(batch)
#     print(f"✅ 为用户 {user_id} 写入推荐 {len(batch)} 条")
