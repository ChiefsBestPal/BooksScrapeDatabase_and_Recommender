// Series Popularity Trends Analysis
// Induced series order: uses publication dates to determine book order in series

MATCH (s:Series)<-[:PART_OF_SERIES]-(b:Book)
WHERE b.averageRating IS NOT NULL AND b.publishedDate IS NOT NULL
WITH s.series_name AS series, 
     b.title AS book_title,
     b.publishedDate AS pub_date, 
     b.averageRating AS rating
ORDER BY series, pub_date
WITH series, 
     collect({
       title: book_title,
       pub_date: pub_date, 
       rating: rating
     }) AS books_data
WITH series,
     [i IN range(0, size(books_data)-1) | 
      {pos: i+1, 
       title: books_data[i].title,
       pub_date: books_data[i].pub_date,
       rating: books_data[i].rating}
     ] AS ordered_books
WHERE size(ordered_books) >= 2  // Only series with 2+ books
WITH series, ordered_books,
     head(ordered_books).rating AS first_rating,
     last(ordered_books).rating AS last_rating,
     reduce(sum = 0.0, book IN ordered_books | sum + book.rating) / size(ordered_books) AS series_avg
RETURN series,
       size(ordered_books) AS book_count,
       round(first_rating * 100) / 100 AS first_book_rating,
       round(last_rating * 100) / 100 AS last_book_rating,
       round(series_avg * 100) / 100 AS series_average,
       round((last_rating - first_rating) * 100) / 100 AS rating_change,
       ordered_books[0..3] AS sample_books,  // Show first few books
       CASE
         WHEN last_rating - first_rating > 0.3 THEN 'Trending Up'
         WHEN last_rating - first_rating < -0.3 THEN 'Trending Down'
         WHEN abs(last_rating - first_rating) <= 0.1 THEN 'Very Stable'
         ELSE 'Moderately Stable'
       END AS trend_category
ORDER BY rating_change DESC, series_average DESC
LIMIT 15;