// ================================================================
// NETWORK ANALYSIS & INFLUENCE QUERIES
// File: 04_network_analysis_queries.cypher
// Description: Analyze collaboration networks, influence patterns, and book relationships
// ================================================================

// ----------------------------------------------------------------
// Query 4.1: Author Collaboration Network (through shared subjects/genres)
// Purpose: Identify authors working in similar domains for collaboration opportunities
// Usage: Adjust minimum shared subjects threshold (currently 2)
// ----------------------------------------------------------------
MATCH (a1:Author)-[:WROTE]->(b1:Book)-[:HAS_SUBJECT]->(s:Subject)<-[:HAS_SUBJECT]-(b2:Book)<-[:WROTE]-(a2:Author)
WHERE a1.author_id < a2.author_id
WITH a1, a2, count(DISTINCT s) as shared_subjects, collect(DISTINCT s.subject_name) as subjects
WHERE shared_subjects >= 2
RETURN a1.person_name as author1,
       a2.person_name as author2,
       shared_subjects,
       subjects[0..5] as common_subjects
ORDER BY shared_subjects DESC
LIMIT 25;

// ----------------------------------------------------------------
// Query 4.2: Genre Influence Network - Which genres lead readers to others
// Purpose: Build genre transition matrix for recommendation systems
// Usage: Minimum transition count (currently 5) can be adjusted for significance
// ----------------------------------------------------------------
MATCH (r:Reviewer)-[rev1:REVIEWED]->(b1:Book)-[:BELONGS_TO_GENRE]->(g1:Genre)
MATCH (r)-[rev2:REVIEWED]->(b2:Book)-[:BELONGS_TO_GENRE]->(g2:Genre)
WHERE g1 <> g2 AND rev1.created < rev2.created
WITH g1, g2, count(r) as transition_count
WHERE transition_count >= 5
WITH g1, g2, transition_count,
     // Calculate percentage of g1 readers who moved to g2
     (transition_count * 100.0 / 
      (MATCH (temp_r:Reviewer)-[:REVIEWED]->(temp_b:Book)-[:BELONGS_TO_GENRE]->(g1) 
       RETURN count(DISTINCT temp_r))) as transition_percentage
RETURN g1.genre_name as from_genre,
       g2.genre_name as to_genre,
       transition_count,
       round(transition_percentage * 100) / 100 as transition_percentage
ORDER BY transition_count DESC
LIMIT 30;

// ----------------------------------------------------------------
// Query 4.3: Book Citation Network (books mentioned together in reviews)
// Purpose: Find books frequently reviewed by the same users (co-occurrence analysis)
// Usage: Minimum shared reviewers (currently 3) indicates significant relationship
// ----------------------------------------------------------------
MATCH (r:Reviewer)-[:REVIEWED]->(b1:Book)
MATCH (r)-[:REVIEWED]->(b2:Book)
WHERE b1.book_id < b2.book_id
WITH b1, b2, count(r) as co_reviewed_by
WHERE co_reviewed_by >= 3
RETURN b1.title as book1,
       b2.title as book2,
       co_reviewed_by as shared_reviewers,
       round(abs(b1.averageRating - b2.averageRating) * 100) / 100 as rating_difference
ORDER BY co_reviewed_by DESC
LIMIT 25;

// ----------------------------------------------------------------
// Query 4.4: Publisher Influence Network
// Purpose: Analyze which publishers have similar book portfolios
// Usage: Identify market competitors and collaboration opportunities
// ----------------------------------------------------------------
MATCH (p1:Publisher)<-[:PUBLISHED_BY]-(b1:Book)-[:BELONGS_TO_GENRE]->(g:Genre)<-[:BELONGS_TO_GENRE]-(b2:Book)-[:PUBLISHED_BY]->(p2:Publisher)
WHERE p1.publisher_id < p2.publisher_id
WITH p1, p2, count(DISTINCT g) as shared_genres, collect(DISTINCT g.genre_name) as genres
WHERE shared_genres >= 3
MATCH (p1)<-[:PUBLISHED_BY]-(pb1:Book)
MATCH (p2)<-[:PUBLISHED_BY]-(pb2:Book)
WITH p1, p2, shared_genres, genres, 
     avg(pb1.averageRating) as p1_avg_rating,
     avg(pb2.averageRating) as p2_avg_rating,
     count(DISTINCT pb1) as p1_book_count,
     count(DISTINCT pb2) as p2_book_count
RETURN p1.publisher_name as publisher1,
       p2.publisher_name as publisher2,
       shared_genres,
       genres[0..5] as common_genres,
       round(p1_avg_rating * 100) / 100 as publisher1_avg_rating,
       round(p2_avg_rating * 100) / 100 as publisher2_avg_rating,
       p1_book_count,
       p2_book_count
ORDER BY shared_genres DESC
LIMIT 20;

// ----------------------------------------------------------------
// Query 4.5: Author Influence Through Reader Transitions
// Purpose: Identify authors who influence readers to explore new authors
// Usage: Track author discovery patterns for recommendation systems
// ----------------------------------------------------------------
MATCH (r:Reviewer)-[rev1:REVIEWED]->(b1:Book)<-[:WROTE]-(a1:Author)
MATCH (r)-[rev2:REVIEWED]->(b2:Book)<-[:WROTE]-(a2:Author)
WHERE a1 <> a2 AND rev1.created < rev2.created
WITH a1, a2, count(r) as readers_transitioned
WHERE readers_transitioned >= 3
RETURN a1.person_name as from_author,
       a2.person_name as to_author,
       readers_transitioned,
       round(readers_transitioned * 100.0 / 
             (MATCH (temp_r:Reviewer)-[:REVIEWED]->(:Book)<-[:WROTE]-(a1) 
              RETURN count(DISTINCT temp_r))) as influence_percentage
ORDER BY readers_transitioned DESC
LIMIT 25;

// ----------------------------------------------------------------
// Query 4.6: Series Connectivity Network
// Purpose: Find series that share similar readership (for cross-promotion)
// Usage: Identify series with overlapping fan bases
// ----------------------------------------------------------------
MATCH (r:Reviewer)-[:REVIEWED]->(b1:Book)-[:PART_OF_SERIES]->(s1:Series)
MATCH (r)-[:REVIEWED]->(b2:Book)-[:PART_OF_SERIES]->(s2:Series)
WHERE s1.series_id < s2.series_id
WITH s1, s2, count(DISTINCT r) as shared_readers
WHERE shared_readers >= 5
MATCH (s1)<-[:PART_OF_SERIES]-(sb1:Book)
MATCH (s2)<-[:PART_OF_SERIES]-(sb2:Book)
WITH s1, s2, shared_readers,
     avg(sb1.averageRating) as s1_avg_rating,
     avg(sb2.averageRating) as s2_avg_rating,
     count(DISTINCT sb1) as s1_book_count,
     count(DISTINCT sb2) as s2_book_count
RETURN s1.series_name as series1,
       s2.series_name as series2,
       shared_readers,
       round(s1_avg_rating * 100) / 100 as series1_avg_rating,
       round(s2_avg_rating * 100) / 100 as series2_avg_rating,
       s1_book_count,
       s2_book_count
ORDER BY shared_readers DESC
LIMIT 20;