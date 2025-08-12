// ================================================================
// ITEM-BASED COLLABORATIVE FILTERING
// Literature Database & Book Recommendation System
// ================================================================

// ----------------------------------------------------------------
//ITEM-ITEM COSINE SIMILARITY  MATRIX
//
// Purpose: Find books that are rated similarly by the same users
// This creates the foundation for item-based collaborative filtering
// ----------------------------------------------------------------

// Basic Item-Item Similarity (Cosine Similarity based on user ratings)
MATCH (b1:Book)<-[r1:REVIEWED]-(u:Reviewer)-[r2:REVIEWED]->(b2:Book)
WHERE b1.book_id < b2.book_id  // Avoid duplicate pairs and self-comparison
  AND r1.rating IS NOT NULL AND r2.rating IS NOT NULL
WITH b1, b2, 
     collect({user: u.reviewer_id, rating1: r1.rating, rating2: r2.rating}) as common_ratings
WHERE size(common_ratings) >= 3  // Minimum 3 users rated both books
WITH b1, b2, common_ratings,
     // Calculate cosine similarity
     reduce(dot_product = 0.0, rating IN common_ratings | 
       dot_product + (rating.rating1 * rating.rating2)) as dot_product,
     sqrt(reduce(sum1 = 0.0, rating IN common_ratings | 
       sum1 + rating.rating1^2)) as norm1,
     sqrt(reduce(sum2 = 0.0, rating IN common_ratings | 
       sum2 + rating.rating2^2)) as norm2,
     size(common_ratings) as common_users
WITH b1, b2, common_users, 
     CASE 
       WHEN norm1 * norm2 > 0 
       THEN dot_product / (norm1 * norm2)
       ELSE 0.0 
     END as cosine_similarity
WHERE cosine_similarity > 0.3  // Only keep reasonably similar items
RETURN b1.title as book1,
       b2.title as book2, 
       common_users,
       round(cosine_similarity * 1000) / 1000 as similarity_score
ORDER BY cosine_similarity DESC
LIMIT 50;


// ----------------------------------------------------------------
// Genre-Aware Item-Based Collaborative Filtering
// Purpose: Enhance recommendations by considering genre preferences
// Combines collaborative filtering with content-based elements
// ----------------------------------------------------------------

WITH 'TARGET_USER_NAME' as target_user_name
MATCH (target_user:Reviewer {person_name: target_user_name})-[target_rating:REVIEWED]->(rated_book:Book)
WHERE target_rating.rating >= 4.0

// Get user's genre preferences
MATCH (rated_book)-[:BELONGS_TO_GENRE]->(preferred_genre:Genre)
WITH target_user, collect(DISTINCT preferred_genre.genre_name) as user_preferred_genres

// Find similar books in preferred genres
MATCH (target_user)-[ur:REVIEWED]->(user_book:Book)
WHERE ur.rating >= 4.0
MATCH (user_book)<-[r1:REVIEWED]-(other_user:Reviewer)-[r2:REVIEWED]->(candidate:Book)
WHERE other_user <> target_user 
  AND NOT (target_user)-[:REVIEWED]->(candidate)
  AND r1.rating >= 4.0 AND r2.rating >= 4.0

// Check if candidate book matches user's genre preferences
MATCH (candidate)-[:BELONGS_TO_GENRE]->(cg:Genre)
WHERE cg.genre_name IN user_preferred_genres

WITH target_user, candidate, user_book,
     count(other_user) as similarity_strength,
     avg(r2.rating) as avg_rating_by_similar_users
     
// Aggregate recommendations by candidate book
WITH candidate, 
     sum(similarity_strength) as total_strength,
     avg(avg_rating_by_similar_users) as predicted_rating,
     collect(user_book.title)[0..3] as based_on_user_books

// Get book details
MATCH (candidate)-[:BELONGS_TO_GENRE]->(g:Genre)
OPTIONAL MATCH (candidate)<-[:WROTE]-(a:Author)

RETURN candidate.title as recommended_book,
       candidate.averageRating as overall_rating,
       candidate.ratingsCount as popularity,
       collect(DISTINCT g.genre_name) as genres,
       collect(DISTINCT a.person_name)[0..2] as authors,
       total_strength as recommendation_confidence,
       round(predicted_rating * 100) / 100 as predicted_user_rating,
       based_on_user_books
ORDER BY total_strength DESC, predicted_rating DESC
LIMIT 20;

// ----------------------------------------------------------------
// Precompute Batch Item Similarity Calculations/Relationships
// Purpose: Pre-calculate item similarities for faster real-time recommendations
// Run this periodically to build a similarity lookup table
// ----------------------------------------------------------------

MATCH (b1:Book)<-[r1:REVIEWED]-(u:Reviewer)-[r2:REVIEWED]->(b2:Book)
WHERE b1.book_id < b2.book_id 
  AND r1.rating IS NOT NULL AND r2.rating IS NOT NULL
  AND b1.ratingsCount >= 10 AND b2.ratingsCount >= 10  // Only popular books

WITH b1, b2, 
     count(u) as common_users,
     avg(abs(r1.rating - r2.rating)) as avg_rating_diff,
     collect({u: u.reviewer_id, r1: r1.rating, r2: r2.rating}) as user_ratings

WHERE common_users >= 3

WITH b1, b2, common_users, avg_rating_diff,
     // Calculate adjusted cosine similarity
     reduce(sum = 0.0, ur IN user_ratings | sum + ur.r1 * ur.r2) / 
     sqrt(reduce(sum1 = 0.0, ur IN user_ratings | sum1 + ur.r1^2) *
          reduce(sum2 = 0.0, ur IN user_ratings | sum2 + ur.r2^2)) as cosine_sim

WITH b1, b2, common_users,
     // Combine cosine similarity with rating agreement
     cosine_sim * (1.0 / (1.0 + avg_rating_diff)) as final_similarity_score

WHERE final_similarity_score > 0.3

// This could be used to CREATE similarity relationships for faster lookup
RETURN b1.book_id as book1_id,
       b1.title as book1_title,
       b2.book_id as book2_id, 
       b2.title as book2_title,
       common_users,
       round(final_similarity_score * 1000) / 1000 as similarity_score
ORDER BY final_similarity_score DESC
LIMIT 1000;