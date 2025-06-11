import os
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from sklearn.metrics.pairwise import cosine_similarity
from recommend.models import RecommendedMovie, User, Movie
from django.db import transaction

# ✅ 获取 JDBC 驱动路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR_PATH = os.path.join(BASE_DIR, "lib", "mysql-connector-j-8.0.33", "mysql-connector-j-8.0.33.jar")

def generate_itemcf_for_user_mysql(user_id: int, top_n: int = 10, sample_fraction: float = 0.01):
    print(f"🎯 使用 PySpark 从 MySQL 为用户 {user_id} 生成推荐")
    print(f"📦 加载 JDBC 驱动路径：{JAR_PATH}")

    # ✅ 启动 Spark
    spark = SparkSession.builder \
        .appName("ItemCF-Recommend") \
        .config("spark.jars", JAR_PATH) \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()

    # ✅ 从 MySQL 读取评分表
    df = spark.read.format("jdbc") \
        .option("url", "jdbc:mysql://localhost:3306/reelrate_db") \
        .option("dbtable", "recommend_rating") \
        .option("user", "root") \
        .option("password", "123456") \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .load() \
        .select("user_id", "movie_id", "score")

    # ✅ 分离当前用户评分和其他用户评分
    user_ratings = df.filter(df["user_id"] == user_id)
    other_ratings = df.filter(df["user_id"] != user_id)

    # ✅ 对其他用户评分进行抽样
    if 0 < sample_fraction < 1:
        print(f"📉 抽样数据：仅保留 {sample_fraction*100:.1f}% 用于推荐训练")
        other_ratings = other_ratings.sample(withReplacement=False, fraction=sample_fraction, seed=42)

    # ✅ 合并当前用户评分和抽样数据
    combined_df = user_ratings.union(other_ratings)

    # ✅ 转换为 Pandas DataFrame
    pdf = combined_df.toPandas()

    if user_id not in pdf["user_id"].unique():
        print(f"⚠ 用户 {user_id} 无评分，跳过推荐")
        spark.stop()
        return

    # ✅ 构建评分矩阵并计算相似度
    matrix = pdf.pivot_table(index="movie_id", columns="user_id", values="score").fillna(0)
    sim_matrix = pd.DataFrame(
        cosine_similarity(matrix),
        index=matrix.index,
        columns=matrix.index
    )

    user_rated = pdf[pdf["user_id"] == user_id].set_index("movie_id")["score"]
    seen_movies = set(user_rated.index)

    scores = {}
    for seen_id, rating in user_rated.items():
        similar_items = sim_matrix[seen_id].drop(index=seen_movies)
        for target_id, sim in similar_items.items():
            scores[target_id] = scores.get(target_id, 0) + rating * sim

    top_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # ✅ 写入推荐结果
    user = User.objects.get(id=user_id)
    RecommendedMovie.objects.filter(user=user).delete()

    batch = []
    for mid, score in top_items:
        try:
            movie = Movie.objects.get(movie_id=mid)
            batch.append(RecommendedMovie(user=user, movie=movie, score=score))
        except Movie.DoesNotExist:
            continue

    with transaction.atomic():
        RecommendedMovie.objects.bulk_create(batch)

    print(f"✅ 为用户 {user_id} 写入推荐 {len(batch)} 条")
    spark.stop()
