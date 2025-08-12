// ================================================================
// MARKET ANALYSIS & ADVANCED INSIGHTS
// File: 05_market_analysis_queries.cypher
// Description: Market saturation, hidden gems, cross-genre analysis, and business insights
// ================================================================

// ----------------------------------------------------------------
// Query 5.1: Market Saturation Analysis by Genre
// Purpose: Understand engagement levels and market opportunities by genre
// Usage: Identifies oversaturated vs. underserved markets
// ----------------------------------------------------------------
MATCH (g:Genre)<-[:BELONGS_TO_GENRE]-(b:Book)
OPTIONAL MATCH (b)<-[:REVIEWED]-(r:Reviewer)
WITH g, count(DISTINCT b) as total_books, 
     count(r) as total_reviews,
     avg(b.averageRating) as avg_genre_rating
RETURN g.genre_name as genre,
       total_books,
       total_reviews,
       round(total_reviews * 1.0 / total_books) as reviews_per_book,
       round(avg_genre_rating * 100) / 100 as avg_rating,
       CASE 
         WHEN total_reviews / total_books > 50 THEN 'Highly Engaged'
         WHEN total_reviews / total_books > 20 THEN 'Well Engaged'
         WHEN total_reviews / total_books > 10 THEN 'Moderately Engaged'
         ELSE 'Low Engagement'
       END as engagement_level
ORDER BY reviews_per_book DESC;

// ----------------------------------------------------------------
// Query 5.2: Hidden Gem Discovery - Underrated High-Quality Books
// Purpose: Find high-quality books with limited exposure for marketing opportunities
// Usage: Adjust rating and review count thresholds to find different tiers of hidden gems
// ----------------------------------------------------------------
MATCH (b:Book)
WHERE b.ratingsCount >= 10 AND b.ratingsCount <= 100 AND b.averageRating >= 4.2
OPTIONAL MATCH (b)-[:BELONGS_TO_GENRE]->(g:Genre)
OPTIONAL MATCH (b)<-[:WROTE]-(a:Author)
RETURN b.title as hidden_gem,
       a.person_name as author,
       b.averageRating as rating,
       b.ratingsCount as ratings_count,
       collect(DISTINCT g.genre_name)[0..3] as genres,
       round((b.averageRating - 3.5) * (101 - b.ratingsCount) / 100 * 100) / 100 as gem_score
ORDER BY gem_score DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 5.3: Author Cross-Genre Success Analysis
// Purpose: Identify versatile authors successful across multiple genres
// Usage: Find authors for cross-genre marketing and collaboration opportunities
// ----------------------------------------------------------------
MATCH (a:Author)-[:WROTE]->(b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
WITH a, g, count(b) as books_in_genre, avg(b.averageRating) as avg_rating_in_genre
WITH a, count(g) as genres_written, collect({genre: g.genre_name, books: books_in_genre, rating: avg_rating_in_genre}) as genre_performance
WHERE genres_written >= 2
RETURN a.person_name as versatile_author,
       genres_written,
       [x IN genre_performance WHERE x.rating >= 4.0] as successful_genres,
       genre_performance
ORDER BY genres_written DESC, size([x IN genre_performance WHERE x.rating >= 4.0]) DESC
LIMIT 15;

// ----------------------------------------------------------------
// Query 5.4: Price Point Analysis and Market Positioning
// Purpose: Analyze pricing strategies and their correlation with ratings/popularity
// Usage: Understand market pricing dynamics (requires price data)
// ----------------------------------------------------------------
MATCH (b:Book)
WHERE b.retailPrice_amount IS NOT NULL AND b.averageRating IS NOT NULL
WITH b,
     CASE 
       WHEN b.retailPrice_amount < 10 THEN 'Budget'
       WHEN b.retailPrice_amount < 20 THEN 'Mid-range'
       WHEN b.retailPrice_amount < 30 THEN 'Premium'
       ELSE 'Luxury'
     END as price_tier
WITH price_tier, 
     count(b) as book_count,
     avg(b.averageRating) as avg_rating,
     avg(b.ratingsCount) as avg_popularity,
     avg(b.retailPrice_amount) as avg_price
RETURN price_tier,
       book_count,
       round(avg_rating * 100) / 100 as average_rating,
       round(avg_popularity) as average_popularity,
       round(avg_price * 100) / 100 as average_price,
       round((avg_rating * avg_popularity) / avg_price * 100) / 100 as value_score
ORDER BY 
  CASE price_tier 
    WHEN 'Budget' THEN 1
    WHEN 'Mid-range' THEN 2
    WHEN 'Premium' THEN 3
    WHEN 'Luxury' THEN 4
  END;

// ----------------------------------------------------------------
// Query 5.5: Competitive Analysis - Publisher Market Share by Genre
// Purpose: Analyze publisher dominance in different genres
// Usage: Identify market leaders and opportunities for smaller publishers
// ----------------------------------------------------------------
MATCH (p:Publisher)<-[:PUBLISHED_BY]-(b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
WITH g, p, count(b) as books_in_genre
WITH g, collect({publisher: p.publisher_name, book_count: books_in_genre}) as publisher_data,
     sum(books_in_genre) as total_books_in_genre
UNWIND publisher_data as pd
WITH g.genre_name as genre,
     pd.publisher as publisher,
     pd.book_count as books,
     total_books_in_genre,
     round(pd.book_count * 100.0 / total_books_in_genre * 100) / 100 as market_share
WHERE market_share >= 5.0  // Only show publishers with significant market share
RETURN genre,
       collect({
         publisher: publisher,
         books: books,
         market_share: market_share
       }) as market_leaders
ORDER BY genre;

// ----------------------------------------------------------------
// Query 5.6: Reader Retention Analysis by Author
// Purpose: Measure how well authors retain readers across their books
// Usage: Identify authors with loyal followings vs. one-hit wonders
// ----------------------------------------------------------------
MATCH (a:Author)-[:WROTE]->(b1:Book)
MATCH (a)-[:WROTE]->(b2:Book)
WHERE b1 <> b2
MATCH (r:Reviewer)-[:REVIEWED]->(b1)
MATCH (r)-[:REVIEWED]->(b2)
WITH a, count(DISTINCT r) as retained_readers,
     count(DISTINCT b1) as total_books_by_author
MATCH (a)-[:WROTE]->(all_books:Book)
WITH a, retained_readers, total_books_by_author,
     count(DISTINCT all_books) as actual_book_count,
     sum(all_books.ratingsCount) as total_reviews_all_books
WHERE actual_book_count >= 2 AND total_reviews_all_books >= 50
RETURN a.person_name as author,
       actual_book_count as books_written,
       retained_readers,
       round(retained_readers * 100.0 / total_reviews_all_books * 100) / 100 as retention_rate,
       CASE 
         WHEN retained_readers * 100.0 / total_reviews_all_books > 20 THEN 'High Loyalty'
         WHEN retained_readers * 100.0 / total_reviews_all_books > 10 THEN 'Medium Loyalty'
         WHEN retained_readers * 100.0 / total_reviews_all_books > 5 THEN 'Low Loyalty'
         ELSE 'One-hit Wonder'
       END as loyalty_category
ORDER BY retention_rate DESC
LIMIT 25;

// ----------------------------------------------------------------
// Query 5.7: Emerging Genre Combinations and Market Trends
// Purpose: Identify trending genre combinations that might represent market opportunities
// Usage: Find innovative genre blends gaining traction
// ----------------------------------------------------------------
MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g1:Genre)
MATCH (b)-[:BELONGS_TO_GENRE]->(g2:Genre)
WHERE g1.genre_name < g2.genre_name AND b.publishedDate IS NOT NULL
WITH g1.genre_name + ' + ' + g2.genre_name as genre_combo,
     date.year(b.publishedDate) as year,
     count(b) as book_count,
     avg(b.averageRating) as avg_rating
WHERE year >= 2015 AND book_count >= 2
WITH genre_combo,
     collect({year: year, count: book_count, rating: avg_rating}) as yearly_data,
     sum(book_count) as total_books,
     avg(avg_rating) as overall_avg_rating
WHERE total_books >= 5
RETURN genre_combo,
       total_books,
       round(overall_avg_rating * 100) / 100 as average_rating,
       yearly_data,
       // Calculate trend direction (are recent years showing growth?)
       CASE 
         WHEN yearly_data[-1].count > yearly_data[0].count THEN 'Growing'
         WHEN yearly_data[-1].count < yearly_data[0].count THEN 'Declining'
         ELSE 'Stable'
       END as trend_direction
ORDER BY total_books DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 5.8: Content Maturity and Target Audience Analysis
// Purpose: Analyze content maturity ratings and their market performance
// Usage: Understand different audience segments and their engagement patterns
// ----------------------------------------------------------------
MATCH (b:Book)
WHERE b.maturityRating IS NOT NULL
WITH b.maturityRating as maturity,
     count(b) as book_count,
     avg(b.averageRating) as avg_rating,
     avg(b.ratingsCount) as avg_reviews,
     sum(b.ratingsCount) as total_reviews
RETURN maturity,
       book_count,
       round(avg_rating * 100) / 100 as average_rating,
       round(avg_reviews) as average_reviews_per_book,
       total_reviews,
       round(total_reviews * 100.0 / (SELECT sum(b2.ratingsCount) FROM (MATCH (b2:Book) WHERE b2.ratingsCount IS NOT NULL))) as market_share_by_reviews
ORDER BY book_count DESC;