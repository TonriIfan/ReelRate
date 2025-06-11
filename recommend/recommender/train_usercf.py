# # recommend/recommender/train_usercf.py
#
# from surprise import Dataset, Reader, KNNBasic
# from surprise.model_selection import train_test_split
# import pandas as pd
# from recommend.models import Rating, RecommendedMovie, User, Movie
# from django.db import transaction
#
# def train_usercf_and_save_recommendations(top_n=10):
#     print("📥 读取评分数据...")
#     data = list(Rating.objects.values_list("user__user_id", "movie__movie_id", "score"))
#     df = pd.DataFrame(data, columns=["user_id", "movie_id", "score"])
#
#     reader = Reader(rating_scale=(0, 5))
#     dataset = Dataset.load_from_df(df[['user_id', 'movie_id', 'score']], reader)
#     trainset = dataset.build_full_trainset()
#
#     print("🧠 训练 UserCF 模型...")
#     sim_options = {'name': 'cosine', 'user_based': True}
#     algo = KNNBasic(sim_options=sim_options)
#     algo.fit(trainset)
#
#     print("🔄 清空旧的推荐结果...")
#     RecommendedMovie.objects.all().delete()
#
#     print("🎯 开始为每个用户生成推荐...")
#     all_user_ids = df['user_id'].unique()
#     all_movie_ids = df['movie_id'].unique()
#     user_rated = df.groupby("user_id")["movie_id"].apply(set).to_dict()
#
#     batch = []
#     for uid in all_user_ids:
#         seen = user_rated.get(uid, set())
#         candidates = [iid for iid in all_movie_ids if iid not in seen]
#
#         predictions = [algo.predict(uid, iid) for iid in candidates]
#         top_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)[:top_n]
#
#         for pred in top_predictions:
#             try:
#                 user = User.objects.get(user_id=pred.uid)
#                 movie = Movie.objects.get(movie_id=pred.iid)
#                 batch.append(RecommendedMovie(user=user, movie=movie, score=pred.est))
#             except Exception as e:
#                 print(f"❗跳过推荐 uid={pred.uid}, iid={pred.iid}：{e}")
#
#     print(f"💾 保存推荐结果，共 {len(batch)} 条")
#     with transaction.atomic():
#         RecommendedMovie.objects.bulk_create(batch)
#
#     print("✅ 推荐生成完毕！")
