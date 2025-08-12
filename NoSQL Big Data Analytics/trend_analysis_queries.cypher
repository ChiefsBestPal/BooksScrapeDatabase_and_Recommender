// ================================================================
// TREND ANALYSIS & TEMPORAL PATTERNS
// File: 03_trend_analysis_queries.cypher
// Description: Analyze publishing trends, author success, and book longevity patterns
// ================================================================

// ----------------------------------------------------------------
// Query 3.1: Publishing Trends by Genre Over Time
// Purpose: Track how different genres have evolved in popularity over years
// Usage: Adjust year range (currently 2000-2023) based on your data
// ----------------------------------------------------------------
MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
WHERE b.publishedDate IS NOT NULL
WITH g, date.year(b.publishedDate) as year, count(b) as books_published
WHERE year >= 2000 AND year <= 2023
RETURN g.genre_name as genre,
       collect({year: year, count: books_published}) as yearly_counts,
       sum(books_published) as total_books
ORDER BY total_books DESC
LIMIT 15;

// ----------------------------------------------------------------
// Query 3.2: Author Productivity and Success Correlation
// Purpose: Analyze relationship between author productivity and book quality/success
// Usage: Minimum book threshold (currently 2) can be adjusted
// ----------------------------------------------------------------
MATCH (a:Author)-[:WROTE]->(b:Book)
WITH a, count(b) as books_written, avg(b.averageRating) as avg_book_rating, sum(b.ratingsCount) as total_ratings
WHERE books_written >= 2
RETURN a.person_name as author,
       books_written,
       round(avg_book_rating * 100) / 100 as avg_rating,
       total_ratings,
       round((avg_book_rating * log(total_ratings + 1)) * 100) / 100 as success_metric
ORDER BY success_metric DESC
LIMIT 25;

// ----------------------------------------------------------------
// Query 3.3: Review Timing Patterns and Book Longevity
// Purpose: Understand how long books stay relevant after publication
// Usage: Adjust time window (currently 10 years) and minimum review threshold
// ----------------------------------------------------------------
MATCH (b:Book)<-[r:REVIEWED]-(reviewer:Reviewer)
WHERE r.created IS NOT NULL AND b.publishedDate IS NOT NULL
WITH b, r, duration.between(b.publishedDate, date(r.created)).days as days_after_publication
WHERE days_after_publication >= 0 AND days_after_publication <= 3650  // Within 10 years
WITH b, 
     count(r) as total_reviews,
     avg(days_after_publication) as avg_review_delay,
     avg(r.rating) as avg_rating
WHERE total_reviews >= 5
RETURN b.title as book,
       b.publishedDate as published,
       total_reviews,
       round(avg_review_delay) as avg_days_to_review,
       round(avg_rating * 100) / 100 as avg_rating,
       CASE 
         WHEN avg_review_delay > 730 THEN 'Evergreen'
         WHEN avg_review_delay > 365 THEN 'Long-lasting'
         WHEN avg_review_delay > 180 THEN 'Sustained'
         ELSE 'Quick-burn'
       END as longevity_category
ORDER BY avg_review_delay DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 3.4: Seasonal Publishing Patterns
// Purpose: Identify seasonal trends in book publishing
// Usage: Useful for understanding publishing industry cycles
// ----------------------------------------------------------------
MATCH (b:Book)
WHERE b.publishedDate IS NOT NULL
WITH date.month(b.publishedDate) as month, count(b) as books_published
RETURN month,
       books_published,
       CASE month
         WHEN 1 THEN 'January'
         WHEN 2 THEN 'February'
         WHEN 3 THEN 'March'
         WHEN 4 THEN 'April'
         WHEN 5 THEN 'May'
         WHEN 6 THEN 'June'
         WHEN 7 THEN 'July'
         WHEN 8 THEN 'August'
         WHEN 9 THEN 'September'
         WHEN 10 THEN 'October'
         WHEN 11 THEN 'November'
         WHEN 12 THEN 'December'
       END as month_name,
       round(books_published * 100.0 / sum(books_published) OVER (), 2) as percentage
ORDER BY month;

// ----------------------------------------------------------------
// Query 3.5: Genre Evolution and Cross-Pollination
// Purpose: Track how genres influence each other over time
// Usage: Identifies emerging genre combinations and trends
// ----------------------------------------------------------------
MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g1:Genre)
MATCH (b)-[:BELONGS_TO_GENRE]->(g2:Genre)
WHERE g1.genre_name < g2.genre_name AND b.publishedDate IS NOT NULL
WITH g1, g2, date.year(b.publishedDate) as year, count(b) as hybrid_books
WHERE year >= 2010 AND hybrid_books >= 2
RETURN g1.genre_name + ' + ' + g2.genre_name as genre_combination,
       collect({year: year, count: hybrid_books}) as yearly_hybrid_counts,
       sum(hybrid_books) as total_hybrid_books
ORDER BY total_hybrid_books DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 3.6: Rating Inflation/Deflation Trends Over Time
// Purpose: Detect if book ratings have changed over time (grade inflation)
// Usage: Helps understand rating system evolution
// ----------------------------------------------------------------
MATCH (b:Book)
WHERE b.publishedDate IS NOT NULL AND b.averageRating IS NOT NULL
WITH date.year(b.publishedDate) as year, avg(b.averageRating) as avg_rating_for_year, count(b) as books_count
WHERE year >= 2000 AND year <= 2023 AND books_count >= 10
RETURN year,
       round(avg_rating_for_year * 100) / 100 as average_rating,
       books_count,
       round((avg_rating_for_year - 3.5) * 100) / 100 as rating_deviation_from_neutral
ORDER BY year;