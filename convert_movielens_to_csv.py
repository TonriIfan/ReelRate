import pandas as pd

def convert_movielens(dat_dir='ml-10M100K', output_csv='ratings_with_tags.csv'):
    print("📥 读取 ratings.dat ...")
    ratings = pd.read_csv(f'{dat_dir}/ratings.dat', sep='::', engine='python',
                          names=['user_id', 'movie_id', 'score', 'timestamp'])

    print("📥 读取 movies.dat ...")
    movies = pd.read_csv(f'{dat_dir}/movies.dat', sep='::', engine='python',
                         names=['movie_id', 'title', 'genres'])

    print("📥 读取 tags.dat ...")
    tags = pd.read_csv(f'{dat_dir}/tags.dat', sep='::', engine='python',
                       names=['user_id', 'movie_id', 'tag', 'timestamp'],
                       dtype={'tag': str},  # 强制为字符串
                       encoding='latin1')  # 防止部分标签报编码错

    # 移除空值
    tags = tags.dropna(subset=['tag'])

    print("🔗 处理标签聚合 ...")
    tag_summary = tags.groupby('movie_id')['tag'].apply(
        lambda x: ' | '.join(set(str(tag).strip() for tag in x if pd.notnull(tag)))
    ).reset_index()

    print("🔗 合并电影信息和标签 ...")
    movies_with_tags = pd.merge(movies, tag_summary, on='movie_id', how='left')
    movies_with_tags.rename(columns={'tag': 'tags'}, inplace=True)

    print("🔗 合并评分和电影信息 ...")
    merged = pd.merge(ratings, movies_with_tags, on='movie_id', how='left')
    final = merged[['user_id', 'movie_id', 'title', 'score', 'genres', 'tags']]

    print("💾 写入 CSV 文件 ...")
    final.to_csv(output_csv, index=False)
    print(f"✅ 转换完成：{output_csv}")


# 执行入口
if __name__ == '__main__':
    convert_movielens()
