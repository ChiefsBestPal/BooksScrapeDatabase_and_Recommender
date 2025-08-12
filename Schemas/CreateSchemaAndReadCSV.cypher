// ================================================================
// LITERATURE DATABASE - NEO4J SCHEMA & IMPORT SCRIPTS
// Based from my final MySQL DDL for BookScrapeDB project
// ================================================================

// ----------------------------------------------------------------
// STEP 1: CREATE CONSTRAINTS & INDEXES
// ----------------------------------------------------------------

// Create uniqueness constraints for main entities
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

// Create indexes for better query performance
CREATE INDEX book_title_index IF NOT EXISTS FOR (b:Book) ON (b.title);
CREATE INDEX book_rating_index IF NOT EXISTS FOR (b:Book) ON (b.averageRating);
CREATE INDEX author_name_index IF NOT EXISTS FOR (a:Author) ON (a.person_name);
CREATE INDEX review_rating_index IF NOT EXISTS FOR ()-[r:REVIEWED]-() ON (r.rating);

// ----------------------------------------------------------------
// STEP 2: IMPORT ENTITY NODES
// ----------------------------------------------------------------

// Import Books (main entity)
LOAD CSV WITH HEADERS FROM 'file:///book.csv' AS row
CREATE (b:Book {
    book_id: toInteger(row.book_id),
    volume_id: row.volume_id,
    ol_book_id: row.ol_book_id,
    ol_work_id: row.ol_work_id,
    title: row.title,
    subtitle: row.subtitle,
    publishedDate: CASE WHEN row.publishedDate =~ '\\d{4}-\\d{2}-\\d{2}' AND NOT row.publishedDate STARTS WITH '0000' 
     THEN date(row.publishedDate) 
     ELSE null 
    END,
    description: row.description,
    isbn_10: row.isbn_10,
    isbn_13: row.isbn_13,
    pageCount: toInteger(row.pageCount),
    content_version: row.content_version,
    viewable_image: toBoolean(row.viewable_image),
    viewable_text: toBoolean(row.viewable_text),
    averageRating: toFloat(row.averageRating),
    ratingsCount: toInteger(row.ratingsCount),
    maturityRating: row.maturityRating,
    language: row.language,
    previewLink: row.previewLink,
    infoLink: row.infoLink,
    pdf_available: toBoolean(row.pdf_available),
    epub_available: toBoolean(row.epub_available),
    book_gid: row.book_gid
});

// Import Persons
LOAD CSV WITH HEADERS FROM 'file:///person.csv' AS row
CREATE (p:Person {
    person_id: toInteger(row.person_id),
    person_name: row.person_name,
    user_gid: row.user_gid
});

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
CREATE (g:Genre {
    genre_id: toInteger(row.genre_id),
    genre_name: row.genre_name
});

// Import Publishers
LOAD CSV WITH HEADERS FROM 'file:///publisher.csv' AS row
CREATE (p:Publisher {
    publisher_id: toInteger(row.publisher_id),
    publisher_name: row.publisher_name
});

// Import Series
LOAD CSV WITH HEADERS FROM 'file:///series.csv' AS row
CREATE (s:Series {
    series_id: toInteger(row.series_id),
    series_name: row.series_name
});

// Import Subjects
LOAD CSV WITH HEADERS FROM 'file:///subject.csv' AS row
CREATE (s:Subject {
    subject_id: toInteger(row.subject_id),
    subject_name: row.subject_name
});

// Import Characters
LOAD CSV WITH HEADERS FROM 'file:///characterr.csv' AS row
CREATE (c:Character {
    character_id: toInteger(row.character_id),
    character_name: row.character_name
});

// Import Places
LOAD CSV WITH HEADERS FROM 'file:///place.csv' AS row
CREATE (p:Place {
    place_id: toInteger(row.place_id),
    place_name: row.place_name
});

// ----------------------------------------------------------------
// STEP 3: CREATE RELATIONSHIPS
// ----------------------------------------------------------------

// Book -> Genre relationships
LOAD CSV WITH HEADERS FROM 'file:///bookgenre.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (g:Genre {genre_id: toInteger(row.genre_id)})
CREATE (b)-[:BELONGS_TO_GENRE]->(g);

// Book -> Subject relationships
LOAD CSV WITH HEADERS FROM 'file:///booksubject.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (s:Subject {subject_id: toInteger(row.subject_id)})
CREATE (b)-[:HAS_SUBJECT]->(s);

// Book -> Publisher relationships
LOAD CSV WITH HEADERS FROM 'file:///bookpublisher.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (p:Publisher {publisher_id: toInteger(row.publisher_id)})
CREATE (b)-[:PUBLISHED_BY]->(p);

// Book -> Character relationships
LOAD CSV WITH HEADERS FROM 'file:///bookcharacter.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (c:Character {character_id: toInteger(row.character_id)})
CREATE (b)-[:FEATURES_CHARACTER]->(c);

// Book -> Place relationships
LOAD CSV WITH HEADERS FROM 'file:///bookplace.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (p:Place {place_id: toInteger(row.place_id)})
CREATE (b)-[:SET_IN_PLACE]->(p);

// Book -> Series relationships
LOAD CSV WITH HEADERS FROM 'file:///bookseries.csv' AS row
MATCH (b:Book {book_id: toInteger(row.book_id)})
MATCH (s:Series {series_id: toInteger(row.series_id)})
CREATE (b)-[:PART_OF_SERIES]->(s);

// Author -> Book relationships
LOAD CSV WITH HEADERS FROM 'file:///bookauthor.csv' AS row
MATCH (a:Author {author_id: toInteger(row.author_id)})
MATCH (b:Book {book_id: toInteger(row.book_id)})
CREATE (a)-[:WROTE]->(b);

// Reviewer -> Book relationships (with review properties)
LOAD CSV WITH HEADERS FROM 'file:///bookreview.csv' AS row
MATCH (r:Reviewer {reviewer_id: toInteger(row.reviewer_id)})
MATCH (b:Book {book_id: toInteger(row.book_id)})
CREATE (r)-[:REVIEWED {
    review_text: row.rev,
    created: CASE 
    WHEN trim(row.created) =~ '\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}' 
    THEN datetime(replace(trim(row.created), ' ', 'T')) 
    ELSE null 
END,
    updated: CASE 
    WHEN trim(row.updated) =~ '\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}' 
    THEN datetime(replace(trim(row.updated), ' ', 'T')) 
    ELSE null 
END,
    likeCount: toInteger(row.likeCount),
    rating: toFloat(row.rating)
}]->(b);

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


