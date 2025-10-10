DELIMITER //

-- Refresh book statistics summary (run nightly)
CREATE PROCEDURE refresh_book_stats()
BEGIN
  TRUNCATE TABLE book_stats_summary;
  
  INSERT INTO book_stats_summary (
    book_id, title, avg_rating, total_reviews, 
    total_ratings, sentiment_avg, genre_list, author_list
  )
  SELECT 
    b.book_id,
    b.title,
    AVG(br.rating) as avg_rating,
    COUNT(DISTINCT br.bookreview_id) as total_reviews,
    b.ratingsCount as total_ratings,
    AVG(br.base_sentiment_score) as sentiment_avg,
    GROUP_CONCAT(DISTINCT g.genre_name SEPARATOR ', ') as genre_list,
    GROUP_CONCAT(DISTINCT p.person_name SEPARATOR ', ') as author_list
  FROM Book b
  LEFT JOIN BookReview br ON b.book_id = br.book_id
  LEFT JOIN BookGenre bg ON b.book_id = bg.book_id
  LEFT JOIN Genre g ON bg.genre_id = g.genre_id
  LEFT JOIN BookAuthor ba ON b.book_id = ba.book_id
  LEFT JOIN Author a ON ba.author_id = a.author_id
  LEFT JOIN Person p ON a.person_id = p.person_id
  GROUP BY b.book_id, b.title, b.ratingsCount;
END //

-- Partition maintenance (add new partitions annually)
CREATE PROCEDURE add_future_partitions()
BEGIN
  DECLARE next_year INT;
  SET next_year = YEAR(CURRENT_DATE()) + 1;
  
  -- Add partition for Book table
  SET @sql = CONCAT(
    'ALTER TABLE Book ADD PARTITION (PARTITION p_', next_year, 
    ' VALUES LESS THAN (', next_year + 1, '))'
  );
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
  
  -- Add partition for BookReview table
  SET @sql = CONCAT(
    'ALTER TABLE BookReview ADD PARTITION (PARTITION p_reviews_', next_year,
    ' VALUES LESS THAN (', next_year + 1, '))'
  );
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END //

DELIMITER ;
