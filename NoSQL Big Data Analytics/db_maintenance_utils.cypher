// ================================================================
// DATABASE MAINTENANCE & UTILITY QUERIES
// File: 07_maintenance_and_utilities.cypher
// Description: Database cleanup, maintenance, and utility functions
// ================================================================

// ----------------------------------------------------------------
// Query 7.1: Database Cleanup - Remove Orphaned Nodes
// Purpose: Clean up nodes that lost their connections due to data issues
// Usage: Run after major data updates or imports
// WARNING: Always backup before running cleanup operations
// ----------------------------------------------------------------

// Remove books without any relationships (orphaned books)
MATCH (b:Book)
WHERE NOT (b)<-[:WROTE]-() 
  AND NOT (b)-[:BELONGS_TO_GENRE]->() 
  AND NOT (b)<-[:REVIEWED]-()
DELETE b;

// Remove authors without books
MATCH (a:Author)
WHERE NOT (a)-[:WROTE]->()
DELETE a;

// Remove reviewers without reviews
MATCH (r:Reviewer)
WHERE NOT (r)-[:REVIEWED]->()
DELETE r;

// ----------------------------------------------------------------
// Query 7.2: Data Standardization and Cleanup
// Purpose: Standardize data formats and clean inconsistencies
// Usage: Data quality maintenance
// ----------------------------------------------------------------

// Standardize book titles (remove extra spaces, capitalize)
MATCH (b:Book)
WHERE b.title CONTAINS "  " OR b.title <> trim(b.title)
SET b.title = trim(b.title)
RETURN count(b) as titles_cleaned;

// Standardize author names
MATCH (a:Author)
WHERE a.person_name <> trim(a.person_name)
SET a.person_name = trim(a.person_name)
RETURN count(a) as author_names_cleaned;

// Fix rating values outside valid range (assuming 1-5 scale)
MATCH (r:Reviewer)-[rev:REVIEWED]->(b:Book)
WHERE rev.rating < 1 OR rev.rating > 5
SET rev.rating = CASE 
    WHEN rev.rating < 1 THEN 1.0
    WHEN rev.rating > 5 THEN 5.0
    ELSE rev.rating
END
RETURN count(rev) as ratings_fixed;

// ----------------------------------------------------------------
// Query 7.3: Index and Constraint Management
// Purpose: Create additional performance indexes based on query patterns
// Usage: Run to optimize database performance for specific use cases
// ----------------------------------------------------------------

// Create composite indexes for common query patterns
CREATE INDEX book_rating_popularity_index IF NOT EXISTS 
FOR (b:Book) ON (b.averageRating, b.ratingsCount);

CREATE INDEX review_rating_date_index IF NOT EXISTS 
FOR ()-[r:REVIEWED]-() ON (r.rating, r.created);

CREATE INDEX book_published_date_index IF NOT EXISTS 
FOR (b:Book) ON (b.publishedDate);

CREATE INDEX author_rating_index IF NOT EXISTS 
FOR (a:Author) ON (a.avgRating);

// Text indexes for search functionality
CREATE TEXT INDEX book_title_text_index IF NOT EXISTS 
FOR (b:Book) ON (b.title);

CREATE TEXT INDEX book_description_text_index IF NOT EXISTS 
FOR (b:Book) ON (b.description);

// ----------------------------------------------------------------
// Query 7.4: Database Statistics and Health Check
// Purpose: Generate comprehensive database health report
// Usage: Regular monitoring and capacity planning
// ----------------------------------------------------------------

// Node distribution
CALL db.labels() YIELD label
CALL apoc.cypher.run("MATCH (n:" + label + ") RETURN count(n) as count", {}) YIELD value
RETURN "Node Count: " + label as metric, value.count as value
ORDER BY value.count DESC

UNION ALL

// Relationship distribution
CALL db.relationshipTypes() YIELD relationshipType
CALL apoc.cypher.run("MATCH ()-[r:" + relationshipType + "]->() RETURN count(r) as count", {}) YIELD value
RETURN "Relationship Count: " + relationshipType as metric, value.count as value
ORDER BY value.count DESC

UNION ALL

// Data quality metrics
MATCH (b:Book) WHERE b.title IS NULL OR b.title = ""
RETURN "Books with missing titles" as metric, count(b) as value

UNION ALL

MATCH (a:Author) WHERE a.person_name IS NULL OR a.person_name = ""
RETURN "Authors with missing names" as metric, count(a) as value

UNION ALL

MATCH ()-[r:REVIEWED]->() WHERE r.rating IS NULL
RETURN "Reviews with missing ratings" as metric, count(r) as value;

// ----------------------------------------------------------------
// Query 7.5: Data Export Utilities
// Purpose: Export data for backup, analysis, or migration
// Usage: Data backup and external analysis
// ----------------------------------------------------------------

// Export book catalog with essential information
MATCH (b:Book)
OPTIONAL MATCH (b)<-[:WROTE]-(a:Author)
OPTIONAL MATCH (b)-[:BELONGS_TO_GENRE]->(g:Genre)
RETURN b.book_id as book_id,
       b.title as title,
       collect(DISTINCT a.person_name) as authors,
       collect(DISTINCT g.genre_name) as genres,
       b.averageRating as rating,
       b.ratingsCount as review_count,
       b.publishedDate as published_date,
       b.isbn_13 as isbn
ORDER BY b.book_id;

// Export review data for sentiment analysis
MATCH (r:Reviewer)-[rev:REVIEWED]->(b:Book)
RETURN rev.rating as rating,
       rev.review_text as review_text,
       rev.created as review_date,
       b.title as book_title,
       r.person_name as reviewer_name
ORDER BY rev.created DESC;

// ----------------------------------------------------------------
// Query 7.6: Data Migration Utilities
// Purpose: Support data migration and transformation operations
// Usage: When restructuring database schema or importing new data
// ----------------------------------------------------------------

// Merge duplicate authors (example - replace with actual duplicate IDs)
MATCH (a1:Author {author_id: 123}), (a2:Author {author_id: 456})
WHERE a1.person_name = a2.person_name
MATCH (a2)-[r:WROTE]->(b:Book)
CREATE (a1)-[:WROTE]->(b)
DELETE r
WITH a1, a2
DELETE a2;

// Update book categories (example: merge similar genres)
MATCH (b:Book)-[r:BELONGS_TO_GENRE]->(g:Genre)
WHERE g.genre_name IN ['Sci-Fi', 'Science Fiction']
MATCH (target:Genre {genre_name: 'Science Fiction'})
CREATE (b)-[:BELONGS_TO_GENRE]->(target)
DELETE r;

// ----------------------------------------------------------------
// Query 7.7: Performance Monitoring Queries
// Purpose: Monitor query performance over time
// Usage: Identify performance degradation and optimization opportunities
// ----------------------------------------------------------------

// Monitor expensive queries (requires query logging enabled)
CALL dbms.listQueries() YIELD queryId, query, elapsedTimeMillis, status
WHERE elapsedTimeMillis > 1000 // Queries taking more than 1 second
RETURN queryId, 
       substring(query, 0, 100) + "..." as query_preview,
       elapsedTimeMillis,
       status
ORDER BY elapsedTimeMillis DESC;

// Cache hit ratio monitoring (if query caching is enabled)
CALL dbms.queryJmx("org.neo4j:instance=kernel#0,name=Page cache") YIELD attributes
RETURN attributes.HitRatio as cache_hit_ratio,
       attributes.Hits as cache_hits,
       attributes.Faults as cache_misses;

// ----------------------------------------------------------------
// Query 7.8: Security and User Management
// Purpose: Manage database security and user access
// Usage: Security maintenance and access control
// ----------------------------------------------------------------

// List all database users and their roles
SHOW USERS YIELD user, roles, suspended
RETURN user, roles, suspended
ORDER BY user;

// Check database privileges
SHOW PRIVILEGES YIELD action, resource, role
RETURN DISTINCT action, resource, role
ORDER BY action, resource;

// ----------------------------------------------------------------
// Query 7.9: Backup and Recovery Verification
// Purpose: Verify database integrity after backup/restore operations
// Usage: Post-backup verification
// ----------------------------------------------------------------

// Verify referential integrity
MATCH (b:Book)<-[:WROTE]-(a:Author)
WITH count(b) as books_with_authors
MATCH (b:Book)
WITH books_with_authors, count(b) as total_books
RETURN total_books, 
       books_with_authors, 
       round(books_with_authors * 100.0 / total_books) as percentage_with_authors;

// Verify review data integrity
MATCH (r:Reviewer)-[rev:REVIEWED]->(b:Book)
WHERE rev.rating IS NOT NULL AND rev.rating >= 1 AND rev.rating <= 5
WITH count(rev) as valid_reviews
MATCH ()-[rev:REVIEWED]->()
WITH valid_reviews, count(rev) as total_reviews
RETURN total_reviews,
       valid_reviews,
       round(valid_reviews * 100.0 / total_reviews) as percentage_valid_reviews;