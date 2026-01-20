// Используем БД analytics
use analytics;

// =========================
// ФИЛЬМЫ + ЛАЙКИ (денорм.)
//
// Один документ = один фильм
// =========================
db.createCollection("movies");

db.movies.createIndex({ movie_id: 1 }, { unique: true });
db.movies.createIndex({ "likes.user_id": 1 });

/*
Пример документа movies:
{
  movie_id: NumberLong,
  likes: [
    {
      user_id: NumberLong,
      rating: NumberInt,
      created_at: ISODate
    }
  ],
  likes_count: NumberInt,
  dislikes_count: NumberInt,
  avg_rating: NumberDouble
}
*/

// =========================
// РЕЦЕНЗИИ
// =========================
db.createCollection("reviews");

db.reviews.createIndex({ review_id: 1 }, { unique: true });
db.reviews.createIndex({ movie_id: 1 });

/*
Пример документа reviews:
{
  review_id: NumberLong,
  movie_id: NumberLong,
  author_id: NumberLong,
  text: String,
  published_at: ISODate,
  user_movie_rating: NumberInt,
  reactions: {
    likes: NumberInt,
    dislikes: NumberInt
  }
}
*/

// =========================
// ЗАКЛАДКИ ПОЛЬЗОВАТЕЛЕЙ
//
// Один документ = один пользователь
// =========================
db.createCollection("user_bookmarks");

db.user_bookmarks.createIndex({ user_id: 1 }, { unique: true });

/*
Пример документа user_bookmarks:
{
  user_id: NumberLong,
  movies: [
    {
      movie_id: NumberLong,
      created_at: ISODate
    }
  ]
}
*/
