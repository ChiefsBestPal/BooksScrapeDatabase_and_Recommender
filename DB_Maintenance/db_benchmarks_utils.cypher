// ================================================================
// PERFORMANCE OPTIMIZATION & VALIDATION QUERIES
// File: 06_performance_optimization_queries.cypher
// Description: Database performance monitoring, data validation, and optimization queries
// ================================================================

// ----------------------------------------------------------------
// Query 6.1: Database Performance Metrics
// Purpose: Monitor database performance and identify optimization opportunities
// Usage: Run periodically to check database health
// ----------------------------------------------------------------

// Count all nodes and relationships
MATCH (n) 
WITH labels(n) as nodeLabels, count(n) as nodeCount
RETURN nodeLabels, nodeCount
ORDER BY nodeCount DESC

UNION ALL

MATCH ()-[r]->() 
WITH type(r) as relType, count(r) as relCount
RETURN [relType] as nodeLabels, relCount as nodeCount
ORDER BY relCount DESC;

// ----------------------------------------------------------------
// Query 6.2: Data Quality Validation
// Purpose: Identify data quality issues and missing information
// Usage: Run after data imports to validate data integrity
// ----------------------------------------------------------------

// Check for missing essential properties
MATCH (b:Book)
WHERE b.title IS NULL OR b.title = ""
RETURN "Books missing titles" as issue, count(b) as count

UNION ALL

MATCH (b:Book)
WHERE b.averageRating IS NULL
RETURN "Books missing ratings" as issue, count(b) as count

UNION ALL

MATCH (a:Author)
WHERE a.person_name IS NULL OR a.person_name = ""
RETURN "Authors missing names" as issue, count(a) as count

UNION ALL

MATCH (r:Reviewer)-[rev:REVIEWED]->(b:Book)
WHERE rev.rating IS NULL
RETURN "Reviews missing ratings" as issue, count(rev) as count;

// ----------------------------------------------------------------
// Query 6.3: Index Usage and Performance Analysis
// Purpose: Analyze query performance and suggest index improvements
// Usage: Identify slow queries and missing indexes
// ----------------------------------------------------------------

// Find books with highest review counts (should use rating index)
PROFILE
MATCH (b:Book)
WHERE b.averageRating >= 4.0
RETURN b.title, b.averageRating, b.ratingsCount
ORDER BY b.ratingsCount DESC
LIMIT 10;

// Find authors by name (should use name index)
PROFILE
MATCH (a:Author)
WHERE a.person_name CONTAINS "Stephen"
RETURN a.person_name, a.avgRating
LIMIT 10;

// ----------------------------------------------------------------
// Query 6.4: Orphaned Nodes Detection
// Purpose: Find nodes that aren't properly connected (data integrity)
// Usage: Clean up incomplete data imports
// ----------------------------------------------------------------

// Books without authors
MATCH (b:Book)
WHERE NOT (b)<-[:WROTE]-(:Author)
RETURN "Books without authors" as issue, count(b) as count, collect(b.title)[0..5] as examples

UNION ALL

// Authors without books
MATCH (a:Author)
WHERE NOT (a)-[:WROTE]->(:Book)
RETURN "Authors without books" as issue, count(a) as count, collect(a.person_name)[0..5] as examples

UNION ALL

// Books without genres
MATCH (b:Book)
WHERE NOT (b)-[:BELONGS_TO_GENRE]->(:Genre)
RETURN "Books without genres" as issue, count(b) as count, collect(b.title)[0..5] as examples;

// ----------------------------------------------------------------
// Query 6.5: Memory Usage Optimization - Large Collection Queries
// Purpose: Optimize queries that might consume excessive memory
// Usage: Use LIMIT and pagination for large result sets
// ----------------------------------------------------------------

// Paginated book recommendations (memory efficient)
MATCH (b:Book)
WHERE b.ratingsCount > 100
WITH b
ORDER BY b.averageRating DESC
SKIP 0 LIMIT 20
RETURN b.title, b.averageRating, b.ratingsCount;

// Memory-efficient author collaboration analysis
MATCH (a1:Author)-[:WROTE]->(b1:Book)-[:HAS_SUBJECT]->(s:Subject)
WITH a1, s, count(b1) as books_in_subject
WHERE books_in_subject >= 2
MATCH (a2:Author)-[:WROTE]->(b2:Book)-[:HAS_SUBJECT]->(s)
WHERE a1.author_id < a2.author_id
WITH a1, a2, count(DISTINCT s) as shared_subjects
WHERE shared_subjects >= 2
RETURN a1.person_name, a2.person_name, shared_subjects
ORDER BY shared_subjects DESC
LIMIT 25;

// ----------------------------------------------------------------
// Query 6.6: Duplicate Detection and Cleanup
// Purpose: Identify potential duplicate entries in the database
// Usage: Data cleaning and quality assurance
// ----------------------------------------------------------------

// Find potential duplicate books (same title, different IDs)
MATCH (b1:Book), (b2:Book)
WHERE b1.book_id < b2.book_id 
  AND b1.title = b2.title 
  AND b1.title IS NOT NULL
RETURN b1.title as duplicate_title,
       collect({id: b1.book_id, isbn: b1.isbn_13, publisher_date: b1.publishedDate}) as book1_info,
       collect({id: b2.book_id, isbn: b2.isbn_13, publisher_date: b2.publishedDate}) as book2_info;

// Find potential duplicate authors (same name, different IDs)
MATCH (a1:Author), (a2:Author)
WHERE a1.author_id < a2.author_id 
  AND a1.person_name = a2.person_name 
  AND a1.person_name IS NOT NULL
RETURN a1.person_name as duplicate_author,
       a1.author_id as id1,
       a2.author_id as id2,
       a1.birthDate as birthdate1,
       a2.birthDate as birthdate2;

// ----------------------------------------------------------------
// Query 6.7: Storage Space Analysis
// Purpose: Understand database storage usage by node and relationship types
// Usage: Capacity planning and storage optimization
// ----------------------------------------------------------------

// Node count analysis
CALL db.labels() YIELD label
CALL apoc.cypher.run("MATCH (n:" + label + ") RETURN count(n) as count", {}) YIELD value
RETURN label, value.count as node_count
ORDER BY value.count DESC;

// Relationship count analysis  
CALL db.relationshipTypes() YIELD relationshipType
CALL apoc.cypher.run("MATCH ()-[r:" + relationshipType + "]->() RETURN count(r) as count", {}) YIELD value
RETURN relationshipType, value.count as relationship_count
ORDER BY value.count DESC;

// ----------------------------------------------------------------
// Query 6.8: Query Performance Benchmarking
// Purpose: Benchmark common query patterns for performance monitoring
// Usage: Regular performance testing to detect regressions
// ----------------------------------------------------------------

// Benchmark: Find books by genre (common recommendation query)
CALL apoc.util.sleep(100) // Small delay to separate from other queries
MATCH (startTime = timestamp())
MATCH (g:Genre {genre_name: 'Fiction'})<-[:BELONGS_TO_GENRE]-(b:Book)
WHERE b.averageRating >= 4.0
WITH b, startTime
ORDER BY b.ratingsCount DESC
LIMIT 10
WITH collect(b.title) as results, startTime
RETURN "Genre search benchmark" as query_type, 
       (timestamp() - startTime) as execution_time_ms,
       size(results) as result_count;

// Benchmark: User similarity calculation (collaborative filtering)
CALL apoc.util.sleep(100)
MATCH (startTime = timestamp())
MATCH (r1:Reviewer {person_name: 'User1'})-[rev1:REVIEWED]->(b:Book)<-[rev2:REVIEWED]-(r2:Reviewer)
WHERE r1 <> r2 AND abs(rev1.rating - rev2.rating) <= 1.0
WITH r1, r2, count(b) as shared_books, startTime
WHERE shared_books >= 2
WITH collect({user: r2.person_name, similarity: shared_books}) as results, startTime
RETURN "User similarity benchmark" as query_type,
       (timestamp() - startTime) as execution_time_ms,
       size(results) as result_count;