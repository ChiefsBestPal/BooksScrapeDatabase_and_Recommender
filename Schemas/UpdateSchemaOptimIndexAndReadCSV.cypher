// ================================================================
// LITERATURE DATABASE - BASE NEO4J SCHEMA & IMPORT SCRIPTS
// Based from base SQL DDL for BookScrapeDB project
// IDEMPOTENT VERSION - Safe to re-run multiple times
// OPTIMIZED FOR: RAG retrieval, rating queries, recommender systems
//
//
// // Quite the same as the other Noe4j schema cypher file but for updates instead of DB creation/restoration
// ================================================================
// ------------------------
//  CONSTRAINTS & INDEXES
// -------------------------

// ===== UNIQUENESS CONSTRAINTS =====
CREATE CONSTRAINT book_id_unique IF NOT EXISTS FOR (b:Book) REQUIRE b.book_id IS UNIQUE;
CREATE CONSTRAINT volume_id_unique IF NOT EXISTS FOR (b:Book) REQUIRE b.volume_id IS UNIQUE;
CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE;
CREATE CONSTRAINT author_id_unique IF NOT EXISTS FOR (a:Author) REQUIRE a.author_id IS UNIQUE;
CREATE CONSTRAINT reviewer_id_unique IF NOT EXISTS FOR (r:Reviewer) REQUIRE r.reviewer_id IS UNIQUE;
CREATE CONSTRAINT genre_id_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.genre_id IS UNIQUE;
CREATE CONSTRAINT publisher_id_unique IF NOT EXISTS FOR (p:Publisher) REQUIRE p.publisher_id IS UNIQUE;
CREATE CONSTRAINT series_id_unique IF NOT EXISTS FOR (s:Series) REQUIRE s.series_id IS UNIQUE;
CREATE CONSTRAINT subject_id_unique IF NOT EXISTS FOR (s:Subject) REQUIRE s.subject_id IS UNIQUE;
CREATE CONSTRAINT character_id_unique IF NOT EXISTS FOR (c:Character) REQUIRE c.character_id IS UNIQUE;
CREATE CONSTRAINT place_id_unique IF NOT EXISTS FOR (p:Place) REQUIRE p.place_id IS UNIQUE;

// ===== RATING OPTIMIZATION INDEXES (for recommender queries) =====
// Range index for book ratings (critical for filtering)
CREATE RANGE INDEX book_rating_range IF NOT EXISTS FOR (b:Book) ON (b.averageRating);
CREATE RANGE INDEX book_ratings_count IF NOT EXISTS FOR (b:Book) ON (b.ratingsCount);

// Range index for review ratings (critical for user preferences)
CREATE RANGE INDEX review_rating_range IF NOT EXISTS FOR ()-[r:REVIEWED]-() ON (r.rating);

// Composite index for rating + count queries (recommender optimization)
CREATE INDEX book_rating_composite IF NOT EXISTS FOR (b:Book) ON (b.averageRating, b.ratingsCount);

// ===== RAG RETRIEVAL OPTIMIZATION INDEXES =====
// Full-text search for book titles and descriptions (semantic search)
CREATE FULLTEXT INDEX book_title_fulltext IF NOT EXISTS 
FOR (b:Book) ON EACH [b.title, b.subtitle];

CREATE FULLTEXT INDEX book_description_fulltext IF NOT EXISTS 
FOR (b:Book) ON EACH [b.description];

// Full-text search for author names (RAG person lookup)
CREATE FULLTEXT INDEX author_name_fulltext IF NOT EXISTS 
FOR (a:Author) ON EACH [a.person_name, a.about];

// Full-text search for genres and subjects (topic-based retrieval)
CREATE FULLTEXT INDEX genre_subject_fulltext IF NOT EXISTS 
FOR (g:Genre|Subject) ON EACH [g.genre_name, g.subject_name];

// ===== STANDARD LOOKUP INDEXES =====
CREATE INDEX book_title_index IF NOT EXISTS FOR (b:Book) ON (b.title);
CREATE INDEX author_name_index IF NOT EXISTS FOR (a:Author) ON (a.person_name);
CREATE INDEX book_language_index IF NOT EXISTS FOR (b:Book) ON (b.language);
CREATE INDEX book_published_date IF NOT EXISTS FOR (b:Book) ON (b.publishedDate);

// ===== RECOMMENDER SYSTEM INDEXES =====
// Index reviewer activity for collaborative filtering
CREATE INDEX reviewer_followers IF NOT EXISTS FOR (r:Reviewer) ON (r.followersCount);
CREATE INDEX author_ratings IF NOT EXISTS FOR (a:Author) ON (a.avgRating);

// Index for date-based queries (review recency)
CREATE RANGE INDEX review_created_date IF NOT EXISTS FOR ()-[r:REVIEWED]-() ON (r.created);
CREATE RANGE INDEX review_updated_date IF NOT EXISTS FOR ()-[r:REVIEWED]-() ON (r.updated);

// ===== VECTOR INDEX FOR EMBEDDINGS (if using RAG with embeddings) =====
// Uncomment when you add embedding properties to books/descriptions
// CREATE VECTOR INDEX book_embedding_index IF NOT EXISTS
// FOR (b:Book) ON (b.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// ------------------------------------
// IMPORT ENTITY NODES
// ------------------------------------

// Import Books (main entity)
LOAD CSV WITH HEADERS FROM 'file:///book.csv' AS row
MERGE (b:Book {book_id: toInteger(row.book_id)})
SET b.volume_id = row.volume_id,
    b.ol_book_id = row.ol_book_id,
    b.ol_work_id = row.ol_work_id,
    b.title = row.title,
    b.subtitle = row.subtitle,
    b.publishedDate = CASE WHEN row.publishedDate =~ '\\d{4}-\\d{2}-\\d{2}' AND NOT row.publishedDate STARTS WITH '0000' 
     THEN date(row.publishedDate) 
     ELSE null 
    END,
    b.description = row.description,
    b.isbn_10 = row.isbn_10,
    b.isbn_13 = row.isbn_13,
    b.pageCount = toInteger(row.pageCount),
    b.content_version = row.content_version,
    b.viewable_image = toBoolean(row.viewable_image),
    b.viewable_text = toBoolean(row.viewable_text),
    b.averageRating = toFloat(row.averageRating),
    b.ratingsCount = toInteger(row.ratingsCount),
    b.maturityRating = row.maturityRating,
    b.language = row.language,
    b.previewLink = row.previewLink,
    b.infoLink = row.infoLink,
    b.pdf_available = toBoolean(row.pdf_available),
    b.epub_available = toBoolean(row.epub_available),
    b.book_gid = row.book_gid;

// Import Persons
LOAD CSV WITH HEADERS FROM 'file:///person.csv' AS row
MERGE (p:Person {person_id: toInteger(row.person_id)})
SET p.person_name = row.person_name,
    p.user_gid = row.user_gid;

// Import Authors (inherits from Person)
LOAD CSV WITH HEADERS FROM 'file:///author.csv' AS row
MATCH (p:Person {person_id: toInteger(row.person_id)})
SET p:Author,
    p.author_id = toInteger(row.author_id),
    p.birthDate = CASE WHEN row.birthDate =~ '\\d{4}-\\d{2}-\\d{2}' AND NOT row.birthDate STARTS WITH '0000' 
     THEN date(row.birthDate) 
     ELSE null 
    END,
    p.deathDate = CASE WHEN row.deathDate =~ '\\d{4}-\\d{2}-\\d{2}' AND NOT row.deathDate STARTS WITH '0000' 
     THEN date(row.deathDate) 
     ELSE null 
    END,
    p.avgRating = toFloat(row.avgRating),
    p.reviewsCount = toInteger(row.reviewsCount),
    p.ratingsCount = toInteger(row.ratingsCount),
    p.about = row.about,
    p.author_gid = row.author_gid;

// Import Reviewers (inherits from Person)
LOAD CSV WITH HEADERS FROM 'file:///reviewer.csv' AS row
MATCH (p:Person {person_id: toInteger(row.person_id)})
SET p:Reviewer,
    p.reviewer_id = toInteger(row.reviewer_id),
    p.followersCount = toInteger(row.followersCount),
    p.isAuthor = toBoolean(row.isAuthor);

// Import Genres
LOAD CSV WITH HEADERS FROM 'file:///genre.csv' AS row
MERGE (g:Genre {genre_id: toInteger(row.genre_id)})
SET g.genre_name = row.genre_name;

// Import Publishers
LOAD CSV WITH HEADERS FROM 'file:///publisher.csv' AS row
MERGE (p:Publisher {publisher_id: toInteger(row.publisher_id)})
SET p.publisher_name = row.publisher_name;

// Import Series
LOAD CSV WITH HEADERS FROM 'file:///series.csv' AS row
MERGE (s:Series {series_id: toInteger(row.series_id)})
SET s.series_name = row.series_name;

// Import Subjects
LOAD CSV WITH HEADERS FROM 'file:///subject.csv' AS row
MERGE (s:Subject {subject_id: toInteger(row.subject_id)})
SET s.subject_name = row.subject_name;

// Import Characters
LOAD CSV WITH HEADERS FROM 'file:///characterr.csv' AS row
MERGE (c:Character {character_id: toInteger(row.character_id)})
SET c.character_name = row.character_name;

// Import Places
LOAD CSV WITH HEADERS FROM 'file:///place.csv' AS row
MERGE (p:Place {place_id: toInteger(row.place_id)})
SET p.place_name = row.place_name;

// -------------------------------
// STEP 3: CREATE RELATIONSHIPS
// ------------------------------

// Book -> Genre relationships
LOAD CSV WITH HEADERS FROM 'file:///bookgenre.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (g:Genre {genre_id: toInteger(row.genre_id)})
MERGE (b)-[:BELONGS_TO_GENRE]->(g);

// Book -> Subject relationships
LOAD CSV WITH HEADERS FROM 'file:///booksubject.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (s:Subject {subject_id: toInteger(row.subject_id)})
MERGE (b)-[:HAS_SUBJECT]->(s);

// Book -> Publisher relationships
LOAD CSV WITH HEADERS FROM 'file:///bookpublisher.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (p:Publisher {publisher_id: toInteger(row.publisher_id)})
MERGE (b)-[:PUBLISHED_BY]->(p);

// Book -> Character relationships
LOAD CSV WITH HEADERS FROM 'file:///bookcharacter.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (c:Character {character_id: toInteger(row.character_id)})
MERGE (b)-[:FEATURES_CHARACTER]->(c);

// Book -> Place relationships
LOAD CSV WITH HEADERS FROM 'file:///bookplace.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (p:Place {place_id: toInteger(row.place_id)})
MERGE (b)-[:SET_IN_PLACE]->(p);

// Book -> Series relationships
LOAD CSV WITH HEADERS FROM 'file:///bookseries.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (s:Series {series_id: toInteger(row.series_id)})
MERGE (b)-[:PART_OF_SERIES]->(s);

// Author -> Book relationships
LOAD CSV WITH HEADERS FROM 'file:///bookauthor.csv' AS row
MATCH (a:Author {author_id: toInteger(row.author_id)})
MATCH (b:Book {book_id: toInteger(row.book_id)})
MERGE (a)-[:WROTE]->(b);

// Reviewer -> Book relationships (with review properties)
LOAD CSV WITH HEADERS FROM 'file:///bookreview.csv' AS row
MATCH (r:Reviewer {reviewer_id: toInteger(row.reviewer_id)})
MATCH (b:Book {book_id: toInteger(row.book_id)})
MERGE (r)-[rev:REVIEWED]->(b)
SET rev.review_text = row.rev,
    rev.created = CASE 
    WHEN trim(row.created) =~ '\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}' 
    THEN datetime(replace(trim(row.created), ' ', 'T')) 
    ELSE null 
END,
    rev.updated = CASE 
    WHEN trim(row.updated) =~ '\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}' 
    THEN datetime(replace(trim(row.updated), ' ', 'T')) 
    ELSE null 
END,
    rev.likeCount = toInteger(row.likeCount),
    rev.rating = toFloat(row.rating);

// ----------------------------------------------------------------
// STEP 4: HANDLE PRICING DATA (as properties or separate nodes)
// ----------------------------------------------------------------

// Add retail price information to books
LOAD CSV WITH HEADERS FROM 'file:///retailprice.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
SET b.retailPrice_amount = toFloat(row.amount),
    b.retailPrice_currency = row.currencyCode;

// Add list price information to books
LOAD CSV WITH HEADERS FROM 'file:///listprice.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
SET b.listPrice_amount = toFloat(row.amount),
    b.listPrice_currency = row.currencyCode;

// Add thumbnail information to books
LOAD CSV WITH HEADERS FROM 'file:///thumbnail.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
SET b.thumbnail_link = row.link;

// ----------------------------------------------------------------
// EXTRA STEP 5: VERIFICATION QUERIES
// ----------------------------------------------------------------

// Verify data import
MATCH (n) RETURN labels(n) as NodeType, count(n) as Count;

// Check relationships
MATCH ()-[r]->() RETURN type(r) as RelationshipType, count(r) as Count;