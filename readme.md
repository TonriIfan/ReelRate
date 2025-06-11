# 🎬 ReelRate - 基于用户评分的个性化电影推荐系统

ReelRate 是一个使用 Django + PySpark 构建的个性化电影推荐系统，结合了真实的 MovieLens 数据集，支持用户注册、评分电影并获取智能推荐结果。
MovieLens训练集下载地址:
> 本项目适合对推荐系统、大数据处理以及 Django 全栈开发感兴趣的开发者学习与实践。

---

## 🚀 快速开始
### 1️⃣ 克隆项目

```bash
git clone https://github.com/TonriIfan/ReelRate.git
cd ReelRate
```
### 2️⃣ 创建虚拟环境 & 安装依赖
```bash
conda create -n MovieRecommand python=3.11
conda activate MovieRecommand
pip install -r requirements.txt
```
> ⚠️ 需要手动下载 PySpark 依赖的 JDBC 驱动文件至 lib/mysql-connector-java-8.0.33.jar
https://dev.mysql.com/downloads/connector/j/
> 

### 3️⃣ 数据准备

    下载数据集：ml-10M.zip

    解压到项目根目录 ./ml-10M100K/

    运行脚本转换为 CSV 格式：
```bash
python convert_movielens_to_csv.py
```

### 🛢️ 导入评分数据（可选：MySQL）
确保 MySQL 运行，并创建数据库 reelrate_db：
```sql
CREATE DATABASE reelrate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
迁移数据
```bash
python manage.py makemigrations
python manage.py migrate
```
导入csv
```bash
python manage.py shell
```
```python
from recommend.import_data import import_ratings_from_csv
import_ratings_from_csv("ratings_with_tags.csv")
```
导入完成后测试
```python
from recommend.models import User, Movie, Rating

print("用户数量：", User.objects.count())
print("电影数量：", Movie.objects.count())
print("评分数量：", Rating.objects.count())

# 随便看一个电影的标签
m = Movie.objects.first()
print(m.title, m.genres, m.tags)
```

### 💡 推荐算法逻辑（ItemCF + Spark）
系统支持如下推荐方式：

    用户注册 → 评分系统抽样电影

    提交评分后自动执行：

        使用 PySpark + MySQL 读取评分表

        构建电影评分矩阵

        使用 cosine_similarity 计算电影相似度

        为当前用户推荐 Top-N 未看过的电影

        写入 RecommendedMovie 表供展示页面读取
```python
recommend/recommender/train_itemcf_mysql.py
```

### 📁 项目结构概览
```csharp
├── ml-10M100K/               # 原始 MovieLens 数据目录
├── convert_movielens_to_csv.py  # 数据转换脚本
├── recommend/
│   ├── models.py             # 数据模型
│   ├── views.py              # 用户注册/评分/推荐逻辑
│   └── recommender/
│       └── train_itemcf_mysql.py  # 推荐算法入口
├── templates/                # 前端页面（index/login/register/rate）
├── static/                  # 样式与动画资源
├── ratings_with_tags.csv    # 转换后的评分数据
└── requirements.txt
```
### ✨ 特色功能

    Apple 风格动画首页（支持 AOS 特效）

    随机抽样评分界面

    推荐系统支持大数据 Spark 架构

    标签增强推荐模型
### 📜 授权协议

本项目基于 MIT 开源许可。