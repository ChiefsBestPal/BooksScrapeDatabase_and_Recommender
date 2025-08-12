// ================================================================
// BOOK RECOMMENDATION ALGORITHMS
// File: 02_recommendation_algorithms.cypher
// Description: Content-based, collaborative, and hybrid recommendation queries
// ================================================================

// ----------------------------------------------------------------
// Query 2.1: Content-Based Filtering - Books Similar to a Given Book
// Purpose: Recommend books based on genre, subject, author, and series similarity
// Usage: Replace 'TARGET_BOOK_TITLE' with the actual book title you want recommendations for
// Parameters: TARGET_BOOK_TITLE (string)
// ----------------------------------------------------------------
MATCH (target:Book {title: 'TARGET_BOOK_TITLE'})
MATCH (target)-[:BELONGS_TO_GENRE]->(g:Genre)<-[:BELONGS_TO_GENRE]-(similar:Book)
OPTIONAL MATCH (target)-[:HAS_SUBJECT]->(s:Subject)<-[:HAS_SUBJECT]-(similar)
OPTIONAL MATCH (target)<-[:WROTE]-(a:Author)-[:WROTE]->(similar)
OPTIONAL MATCH (target)-[:PART_OF_SERIES]->(series:Series)<-[:PART_OF_SERIES]-(similar)
WHERE similar <> target
WITH similar, target,
     count(DISTINCT g) as genre_overlap,
     count(DISTINCT s) as subject_overlap,
     count(DISTINCT a) as author_overlap,
     count(DISTINCT series) as series_overlap
WITH similar, target,
     (genre_overlap * 2 + subject_overlap * 1.5 + author_overlap * 3 + series_overlap * 4) as similarity_score
WHERE similarity_score > 0
RETURN similar.title as recommended_book,
       similar.averageRating as rating,
       similar.ratingsCount as popularity,
       similarity_score,
       round(abs(similar.averageRating - target.averageRating) * 100) / 100 as rating_difference
ORDER BY similarity_score DESC, similar.averageRating DESC
LIMIT 15;

// ----------------------------------------------------------------
// Query 2.2: Collaborative Filtering - User-Based Recommendations
// Purpose: Find books liked by users with similar taste to a target reviewer
// Usage: Replace 'TARGET_REVIEWER_NAME' with actual reviewer name
// Parameters: TARGET_REVIEWER_NAME (string)
// ----------------------------------------------------------------
MATCH (target:Reviewer {person_name: 'TARGET_REVIEWER_NAME'})
MATCH (target)-[t_rev:REVIEWED]->(b:Book)<-[o_rev:REVIEWED]-(other:Reviewer)
WHERE abs(t_rev.rating - o_rev.rating) <= 1.0 AND target <> other
WITH other, count(b) as shared_books, avg(abs(t_rev.rating - o_rev.rating)) as avg_diff
WHERE shared_books >= 2
ORDER BY shared_books DESC, avg_diff ASC
LIMIT 10
MATCH (other)-[rec_rev:REVIEWED]->(rec_book:Book)
WHERE rec_rev.rating >= 4.0 AND NOT (target)-[:REVIEWED]->(rec_book)
RETURN rec_book.title as recommendation,
       rec_book.averageRating as book_rating,
       rec_rev.rating as recommender_rating,
       other.person_name as similar_user,
       shared_books as similarity_strength
ORDER BY rec_rev.rating DESC, book_rating DESC
LIMIT 10;

// ----------------------------------------------------------------
// Query 2.3: Hybrid Recommendation with Popularity Boost
// Purpose: Combine content similarity with popularity metrics for balanced recommendations
// Usage: Adjust rating and review count thresholds as needed
// ----------------------------------------------------------------
MATCH (b:Book)
WHERE b.ratingsCount > 50 AND b.averageRating > 3.5
OPTIONAL MATCH (b)-[:BELONGS_TO_GENRE]->(g:Genre)
OPTIONAL MATCH (b)<-[:WROTE]-(a:Author)
WITH b, collect(DISTINCT g.genre_name) as genres, collect(DISTINCT a.person_name) as authors
RETURN b.title as book,
       b.averageRating as rating,
       b.ratingsCount as popularity,
       round((b.averageRating * 0.7 + log(b.ratingsCount) * 0.3) * 100) / 100 as recommendation_score,
       genres[0..3] as main_genres,
       authors[0..2] as main_authors
ORDER BY recommendation_score DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 2.4: Book-to-Book Similarity Matrix (for item-based collaborative filtering)
// Purpose: Calculate similarity scores between books for item-based filtering
// Usage: Use results to build similarity lookup tables
// ----------------------------------------------------------------
MATCH (b1:Book)-[:BELONGS_TO_GENRE]->(g:Genre)<-[:BELONGS_TO_GENRE]-(b2:Book)
WHERE b1.book_id < b2.book_id
OPTIONAL MATCH (b1)-[:HAS_SUBJECT]->(s:Subject)<-[:HAS_SUBJECT]-(b2)
OPTIONAL MATCH (b1)<-[:WROTE]-(a:Author)-[:WROTE]->(b2)
WITH b1, b2,
     count(DISTINCT g) as genre_similarity,
     count(DISTINCT s) as subject_similarity,
     count(DISTINCT a) as author_similarity,
     abs(b1.averageRating - b2.averageRating) as rating_difference
WITH b1, b2,
     (genre_similarity * 1.0 + subject_similarity * 1.5 + author_similarity * 3.0) / 
     (1.0 + 1.5 + 3.0) as content_similarity,
     1.0 / (1.0 + rating_difference) as rating_similarity
WHERE content_similarity > 0
RETURN b1.title as book1,
       b2.title as book2,
       round(content_similarity * 100) / 100 as content_sim,
       round(rating_similarity * 100) / 100 as rating_sim,
       round((content_similarity * 0.7 + rating_similarity * 0.3) * 100) / 100 as overall_similarity
ORDER BY overall_similarity DESC
LIMIT 50;

// ----------------------------------------------------------------
// Query 2.5: Genre-Based Recommendations for New Users (Cold Start Problem)
// Purpose: Recommend popular books from preferred genres for users with limited history
// Usage: Replace genre list with user's indicated preferences
// ----------------------------------------------------------------
WITH ['Fiction', 'Science Fiction', 'Fantasy'] as preferred_genres
MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
WHERE g.genre_name IN preferred_genres
WITH b, g, b.averageRating * log(b.ratingsCount + 1) as popularity_score
WHERE b.ratingsCount >= 20 AND b.averageRating >= 4.0
RETURN b.title as recommended_book,
       g.genre_name as genre,
       b.averageRating as rating,
       b.ratingsCount as review_count,
       round(popularity_score * 100) / 100 as recommendation_score
ORDER BY recommendation_score DESC
LIMIT 15;