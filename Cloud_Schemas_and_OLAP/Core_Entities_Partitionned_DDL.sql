-- ----------------------------------------------------------------------------
-- Please refer to base schemas in "Schemas/" 's README for intutive order of execution and base logic
-- These tables are optimized for OLAP + Cloud Lakes hybrid etc...

-- SCALING NOTE:
-- while these work great for dimensional analysis in Big Query + CloudSQL engines 
-- and integrate well with noSQL ML/AI + Big Data workflows..
-- If need more than batch ETL operations or scale into large cloud/CDN,
-- consider denormalizing table model architecture and also make scheduled job proc to re-index,re-cluster etc...
-- FOR MORE PEOPLE... base plate here will work great
-- ----------------------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS LiteratureScrapeDB 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE LiteratureScrapeDB;

-- ----------------------------------------------------------------------------
-- Book, Person base table (Generic user), Reviewer person, author person, BookReview (LARGEST IN TERMS OF SHEER SIZE)
-- This Schema / Def contains all needed partitions, cluster-ready (innodb sql.. but auto in Big Query GCP Cloud SQL)
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- CENTRAL/MAIN ENTITY: Book 
-- (Partitioned by publishedDate year... Can change cluster+partition if requirements are different)
-- ----------------------------------------------------------------------------
CREATE TABLE Book (
  book_id BIGINT AUTO_INCREMENT,
  volume_id VARCHAR(255),
  ol_book_id VARCHAR(255),
  ol_work_id VARCHAR(200),
  title VARCHAR(500) NOT NULL,  -- Increased for long titles
  subtitle VARCHAR(500),
  publishedDate DATE NOT NULL DEFAULT '1900-01-01',  -- Required for partitioning
  description TEXT,
  isbn_10 VARCHAR(20),
  isbn_13 VARCHAR(20),
  pageCount INT,
  content_version VARCHAR(50),
  viewable_image BOOLEAN DEFAULT FALSE,
  viewable_text BOOLEAN DEFAULT FALSE,
  averageRating FLOAT,
  ratingsCount INT DEFAULT 0,
  maturityRating VARCHAR(50),
  language VARCHAR(10),
  previewLink VARCHAR(500),
  infoLink VARCHAR(500),
  pdf_available BOOLEAN DEFAULT FALSE,
  epub_available BOOLEAN DEFAULT FALSE,
  book_gid VARCHAR(255),
  
  -- Metadata for data lineage
  source VARCHAR(50) COMMENT 'goodreads, google-books, openlibrary',
  ingestion_date DATE DEFAULT (CURRENT_DATE),
  data_version INT DEFAULT 1,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (book_id, publishedDate),  -- Composite for partitioning
  UNIQUE KEY idx_volume_id (volume_id),
  UNIQUE KEY idx_ol_book_id (ol_book_id),
  UNIQUE KEY idx_ol_work_id (ol_work_id),
  UNIQUE KEY idx_book_gid (book_gid),
  
  -- Covering indexes for common queries
  INDEX idx_title_rating (title(100), averageRating),
  INDEX idx_language_date (language, publishedDate),
  INDEX idx_isbn (isbn_13, isbn_10),
  INDEX idx_source_ingestion (source, ingestion_date)
)
ENGINE=InnoDB
PARTITION BY RANGE (YEAR(publishedDate)) (
  PARTITION p_pre_1900 VALUES LESS THAN (1900),
  PARTITION p_1900_1950 VALUES LESS THAN (1950),
  PARTITION p_1950_1980 VALUES LESS THAN (1980),
  PARTITION p_1980_2000 VALUES LESS THAN (2000),
  PARTITION p_2000_2010 VALUES LESS THAN (2010),
  PARTITION p_2010_2015 VALUES LESS THAN (2015),
  PARTITION p_2015_2020 VALUES LESS THAN (2020),
  PARTITION p_2020_2025 VALUES LESS THAN (2025),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- ----------------------------------------------------------------------------
-- Person (Base table for Authors & Reviewers)
-- ----------------------------------------------------------------------------
CREATE TABLE Person (
  person_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  person_name VARCHAR(255) NOT NULL,
  user_gid VARCHAR(255),
  person_type ENUM('author', 'reviewer', 'both') DEFAULT 'reviewer',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY idx_user_gid (user_gid),
  INDEX idx_person_name (person_name(100)),
  INDEX idx_person_type (person_type)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Author (Partitioned by avgRating for performance queries)
-- 
-- ----------------------------------------------------------------------------
CREATE TABLE Author (
  author_id BIGINT AUTO_INCREMENT,
  person_id BIGINT NOT NULL,
  birthDate DATE,
  deathDate DATE,
  avgRating FLOAT DEFAULT 0.0,
  reviewsCount INT DEFAULT 0,
  ratingsCount INT DEFAULT 0,
  about TEXT,
  author_gid VARCHAR(255),
  base_popularity_score FLOAT GENERATED ALWAYS AS (
    LOG10(1 + ratingsCount) * avgRating
  ) STORED COMMENT 'Computed popularity metric',
  
  PRIMARY KEY (author_id, avgRating),  -- Composite for partition
  UNIQUE KEY idx_person_id (person_id),
  UNIQUE KEY idx_author_gid (author_gid),
  INDEX idx_ratings (ratingsCount, avgRating),
  INDEX idx_bpopularity (base_popularity_score),
  
  FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
)
ENGINE=InnoDB
PARTITION BY RANGE (FLOOR(avgRating)) (
  PARTITION p_rating_0_2 VALUES LESS THAN (2),
  PARTITION p_rating_2_3 VALUES LESS THAN (3),
  PARTITION p_rating_3_4 VALUES LESS THAN (4),
  PARTITION p_rating_4_5 VALUES LESS THAN (5),
  PARTITION p_rating_5_plus VALUES LESS THAN MAXVALUE
);

-- ----------------------------------------------------------------------------
-- Reviewer
-- ----------------------------------------------------------------------------
CREATE TABLE Reviewer (
  reviewer_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  person_id BIGINT NOT NULL,
  followersCount INT DEFAULT 0,
  isAuthor BOOLEAN DEFAULT FALSE,
  base_influence_score FLOAT GENERATED ALWAYS AS (
    LOG10(1 + followersCount)
  ) STORED,
  
  UNIQUE KEY idx_person_id (person_id),
  INDEX idx_followers (followersCount DESC),
  INDEX idx_binfluence (base_influence_score DESC),
  
  FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
) ENGINE=InnoDB;
-- ----------------------------------------------------------------------------
-- BookReview (LARGEST TABLE - Partitioned by review date)
-- ----------------------------------------------------------------------------
CREATE TABLE BookReview (
  bookreview_id BIGINT AUTO_INCREMENT,
  reviewer_id BIGINT NOT NULL,
  book_id BIGINT NOT NULL,
  rev TEXT,
  created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  likeCount INT DEFAULT 0,
  rating FLOAT,
  base_sentiment_score FLOAT COMMENT 'NLP sentiment: -1 (negative) to +1 (positive)',
  
  PRIMARY KEY (bookreview_id, created),  -- Composite for partitioning
  INDEX idx_reviewer_book (reviewer_id, book_id),
  INDEX idx_book_rating (book_id, rating),
  INDEX idx_sentiment (base_sentiment_score),
  INDEX idx_popular_reviews (likeCount DESC, created DESC),
  
  FOREIGN KEY (reviewer_id) REFERENCES Reviewer(reviewer_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
)
ENGINE=InnoDB
PARTITION BY RANGE (YEAR(created)) (
  PARTITION p_reviews_2010 VALUES LESS THAN (2010),
  PARTITION p_reviews_2015 VALUES LESS THAN (2015),
  PARTITION p_reviews_2020 VALUES LESS THAN (2020),
  PARTITION p_reviews_2021 VALUES LESS THAN (2021),
  PARTITION p_reviews_2022 VALUES LESS THAN (2022),
  PARTITION p_reviews_2023 VALUES LESS THAN (2023),
  PARTITION p_reviews_2024 VALUES LESS THAN (2024),
  PARTITION p_reviews_2025 VALUES LESS THAN (2025),
  PARTITION p_reviews_future VALUES LESS THAN MAXVALUE
);