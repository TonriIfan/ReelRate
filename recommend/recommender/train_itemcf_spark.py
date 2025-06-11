# # recommend/recommender/train_itemcf_spark.py
#
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col, lit
# from sklearn.metrics.pairwise import cosine_similarity
# import pandas as pd
# from recommend.models import RecommendedMovie, Movie, User
# from django.db import transaction
#
# def generate_itemcf_for_user_spark(csv_path, user_id, top_n=10):
#     spark = SparkSession.builder.appName("ItemCF").getOrCreate()
#
#     # 读取评分数据 CSV
#     df = spark.read.csv(csv_path, header=True, inferSchema=True)
#     pdf = df.toPandas()
#     spark.stop()
#
#     if pdf[pdf["user_id"] == user_id].empty:
#         print(f"⚠ 用户 {user_id} 没有评分，跳过推荐")
#         return
#
#     # 构建评分矩阵
#     matrix = pdf.pivot_table(index="movie_id", columns="user_id", values="score").fillna(0)
#
#     # 计算物品相似度
#     similarity_matrix = pd.DataFrame(
#         cosine_similarity(matrix),
#         index=matrix.index,
#         columns=matrix.index
#     )
#
#     # 获取当前用户评分记录
#     user_rated = pdf[pdf["user_id"] == user_id].set_index("movie_id")["score"]
#     seen_movies = set(user_rated.index)
#
#     # 基于相似度加权推荐
#     scores = {}
#     for seen_id, rating in user_rated.items():
#         similar_items = similarity_matrix[seen_id].drop(index=seen_movies)
#         for target_id, sim in similar_items.items():
#             scores[target_id] = scores.get(target_id, 0) + rating * sim
#
#     # 排序 Top-N 推荐
#     ranked_movies = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
#
#     # 写入数据库
#     user = User.objects.get(id=user_id)
#     RecommendedMovie.objects.filter(user=user).delete()
#
#     batch = []
#     for mid, score in ranked_movies:
#         try:
#             movie = Movie.objects.get(movie_id=mid)
#             batch.append(RecommendedMovie(user=user, movie=movie, score=score))
#         except Movie.DoesNotExist:
#             continue
#
#     with transaction.atomic():
#         RecommendedMovie.objects.bulk_create(batch)
#
#     print(f"✅ 为用户 {user_id} 写入推荐 {len(batch)} 条")
