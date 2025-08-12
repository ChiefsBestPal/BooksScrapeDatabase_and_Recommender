// ================================================================
// USER PROFILING & SENTIMENT ANALYSIS QUERIES
// File: 01_user_profiling_queries.cypher
// Description: Analyze reviewer behavior, preferences, and authority
// ================================================================

// ----------------------------------------------------------------
// Query 1.1: Comprehensive Reviewer Profiles with Reading Preferences
// Purpose: Build detailed user profiles showing genre preferences and reading patterns
// Usage: Replace LIMIT value based on your needs
// ----------------------------------------------------------------
MATCH (r:Reviewer)-[rev:REVIEWED]->(b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
WITH r, g, 
     avg(rev.rating) as avg_genre_rating,
     count(rev) as books_reviewed_in_genre,
     collect(DISTINCT b.title) as books_in_genre
RETURN r.person_name as reviewer,
       r.followersCount as influence,
       collect({
         genre: g.genre_name,
         avg_rating: round(avg_genre_rating * 100) / 100,
         books_count: books_reviewed_in_genre,
         sample_books: books_in_genre[0..3]
       }) as genre_preferences
ORDER BY r.followersCount DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 1.2: Sentiment Network Analysis - Reviewers with Similar Tastes
// Purpose: Find reviewers with similar rating patterns for collaborative filtering
// Usage: Adjust rating difference threshold (currently 1.0) and minimum shared books (currently 3)
// ----------------------------------------------------------------
MATCH (r1:Reviewer)-[rev1:REVIEWED]->(b:Book)<-[rev2:REVIEWED]-(r2:Reviewer)
WHERE r1.reviewer_id < r2.reviewer_id AND 
      abs(rev1.rating - rev2.rating) <= 1.0
WITH r1, r2, 
     count(b) as shared_books,
     avg(abs(rev1.rating - rev2.rating)) as avg_rating_diff,
     collect({book: b.title, r1_rating: rev1.rating, r2_rating: rev2.rating}) as shared_reviews
WHERE shared_books >= 3
RETURN r1.person_name as reviewer1,
       r2.person_name as reviewer2,
       shared_books,
       round(avg_rating_diff * 100) / 100 as rating_similarity,
       shared_reviews[0..5] as sample_agreements
ORDER BY shared_books DESC, avg_rating_diff ASC
LIMIT 25;

// ----------------------------------------------------------------
// Query 1.3: Reviewer Authority Score (PageRank-style)
// Purpose: Calculate influence scores for reviewers based on multiple factors
// Usage: Weights can be adjusted in the formula (followers + likes*0.5 + reviews*0.2)
// ----------------------------------------------------------------
MATCH (r:Reviewer)
WITH r, r.followersCount + r.ratingsCount * 0.1 as base_score
MATCH (r)-[rev:REVIEWED]->(b:Book)
WITH r, base_score, 
     avg(rev.rating) as avg_rating,
     count(rev) as review_count,
     sum(rev.likeCount) as total_likes
RETURN r.person_name as reviewer,
       round((base_score + total_likes * 0.5 + review_count * 0.2) * 100) / 100 as authority_score,
       r.followersCount as followers,
       review_count,
       round(avg_rating * 100) / 100 as avg_rating_given
ORDER BY authority_score DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 1.4: User Diversity Score - How diverse are reviewer's reading habits
// Purpose: Measure reading diversity for personalization algorithms
// Usage: Minimum book threshold (currently 5) can be adjusted
// ----------------------------------------------------------------
MATCH (r:Reviewer)-[:REVIEWED]->(b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
WITH r, count(DISTINCT g) as unique_genres, count(b) as total_books
WHERE total_books >= 5
RETURN r.person_name as reviewer,
       total_books,
       unique_genres,
       round(unique_genres * 1.0 / total_books * 100) / 100 as diversity_score,
       CASE 
         WHEN unique_genres * 1.0 / total_books > 0.8 THEN 'Very Diverse'
         WHEN unique_genres * 1.0 / total_books > 0.6 THEN 'Diverse'
         WHEN unique_genres * 1.0 / total_books > 0.4 THEN 'Somewhat Diverse'
         ELSE 'Specialized'
       END as diversity_category
ORDER BY diversity_score DESC
LIMIT 20;