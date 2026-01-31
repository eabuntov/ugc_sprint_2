-- База данных
CREATE DATABASE IF NOT EXISTS analytics;
USE analytics;

-- =========================
-- ЛАЙКИ ФИЛЬМОВ (оценки 0–10)
-- =========================
CREATE TABLE IF NOT EXISTS movie_likes
(
    user_id UInt64,
    movie_id UInt64,
    rating UInt8,
    created_at DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (movie_id, user_id)
SETTINGS index_granularity = 8192;

-- =========================
-- РЕЦЕНЗИИ К ФИЛЬМАМ
-- =========================
CREATE TABLE IF NOT EXISTS reviews
(
    review_id UInt64,
    movie_id UInt64,
    author_id UInt64,
    review_text String,
    user_movie_rating UInt8,
    published_at DateTime
)
ENGINE = MergeTree
ORDER BY (movie_id, review_id)
SETTINGS index_granularity = 8192;

-- =========================
-- ЛАЙКИ / ДИЗЛАЙКИ РЕЦЕНЗИЙ
-- =========================
CREATE TABLE IF NOT EXISTS review_reactions
(
    review_id UInt64,
    user_id UInt64,
    is_like UInt8,       -- 1 = like, 0 = dislike
    created_at DateTime
)
ENGINE = MergeTree
ORDER BY (review_id, user_id)
SETTINGS index_granularity = 8192;

-- =========================
-- ЗАКЛАДКИ ПОЛЬЗОВАТЕЛЕЙ
-- =========================
CREATE TABLE IF NOT EXISTS bookmarks
(
    user_id UInt64,
    movie_id UInt64,
    created_at DateTime
)
ENGINE = MergeTree
ORDER BY (user_id, movie_id)
SETTINGS index_granularity = 8192;
