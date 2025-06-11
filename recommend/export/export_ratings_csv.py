# recommend/export/export_ratings_csv.py

import csv
from django.db import connection
from tqdm import tqdm

def export_ratings_csv(path="ratings.csv", batch_size=10000):
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "movie_id", "score"])

        cursor = connection.cursor()

        # 获取总记录数
        cursor.execute("SELECT COUNT(*) FROM recommend_rating")
        total = cursor.fetchone()[0]

        # 开始分页查询
        offset = 0
        pbar = tqdm(total=total, desc="导出评分数据")

        while offset < total:
            cursor.execute(f"""
                SELECT user_id, movie_id, score
                FROM recommend_rating
                LIMIT {batch_size} OFFSET {offset}
            """)
            rows = cursor.fetchall()
            if not rows:
                break
            writer.writerows(rows)
            offset += len(rows)
            pbar.update(len(rows))

        pbar.close()
        print(f"✅ 导出完成：{path}，共 {total} 条记录")
