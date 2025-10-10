-- This a minimal DDL to allow OLAP and SQL ACID compliant analysis on Google cloud
-- you could add a lot of dimensions like books' characters (See entities DDL) for very in depth Multi-dim... but this is the boilerplate
-- NB: REPLACE 'your-project' with your Google Cloud project name. 
-- NB: YOU CAN use BQ cli to directly load a lot of this
--     your lake/cloud unstructured storage's blobs/buckets etc.. can be loaded with csv or json..
--     and parquet is common with Spark and Big data scale flows.
--     HOWEVER.. It is possible to efficiently load from ETL directly into BQ for direct use in your Warehouse
--     So when doing SQL's server,ddl and query tuning, keep in mind that BQ infra mostly
-- NB: Similar to BQ line above, Neo4j (Graph DB book analytics platform) can be loaded with raw CSV or with Neo4J-ETL
--     Also keep this in mind when tuning in specific cases.
--     For Neo4J Cypher CREATE/MERGE 'DDL' scripts see "Schemas/"

-- Create BQ-native dataset
CREATE SCHEMA IF NOT EXISTS `your-project.bookscraperdb`
OPTIONS(
  location="US",
  description="Literature analytics warehouse"
);

-- Books table (Partitioned + Clustered)
CREATE TABLE `your-project.bookscraperdb.books`
(
  book_id INT64,
  volume_id STRING,
  ol_book_id STRING,
  ol_work_id STRING,
  title STRING NOT NULL,
  subtitle STRING,
  publishedDate DATE,
  description STRING,
  isbn_10 STRING,
  isbn_13 STRING,
  pageCount INT64,
  averageRating FLOAT64,
  ratingsCount INT64,
  language STRING,
  
  -- Nested/Repeated fields (BigQuery specialty)
  authors ARRAY<STRUCT<author_id INT64, name STRING, avgRating FLOAT64>>,
  genres ARRAY<STRING>,
  subjects ARRAY<STRING>,
  
  -- Metadata
  source STRING OPTIONS(description="goodreads, google-books, openlibrary"),
  ingestion_date DATE NOT NULL,
  data_version INT64 DEFAULT 1
)
PARTITION BY ingestion_date
CLUSTER BY book_id, publishedDate, language
OPTIONS(
  description="Books dimension with historical tracking",
  partition_expiration_days=null,  -- Keep forever
  require_partition_filter=false
);

-- Reviews fact table (Heavy partitioning for scale)
CREATE TABLE `your-project.bookscraperdb.reviews`
(
  review_id INT64,
  book_id INT64,
  reviewer_id INT64,
  rating FLOAT64,
  review_text STRING,
  review_date DATE NOT NULL,
  created_datetime TIMESTAMP,
  likeCount INT64,
  base_sentiment_score FLOAT64,
  
  -- Denormalized for query performance
  book_title STRING,
  reviewer_name STRING,
  
  ingestion_date DATE
)
PARTITION BY review_date  -- Partition by review date (temporal queries)
CLUSTER BY book_id, reviewer_id, rating
OPTIONS(
  description="Reviews fact table",
  partition_expiration_days=null
);

-- Authors dimension
CREATE TABLE `your-project.bookscraperdb.authors`
(
  author_id INT64,
  person_id INT64,
  author_name STRING,
  author_gid STRING,
  birthDate DATE,
  deathDate DATE,
  avgRating FLOAT64,
  reviewsCount INT64,
  ratingsCount INT64,
  about STRING,
  
  -- Computed fields
  base_popularity_score FLOAT64,
  is_active BOOL,
  
  ingestion_date DATE
)
PARTITION BY ingestion_date
CLUSTER BY author_id, avgRating
OPTIONS(
  description="Authors dimension"
);

-- Materialized view for OLAP (auto-refresh)
CREATE MATERIALIZED VIEW `your-project.bookscraperdb.books_with_stats` AS
SELECT 
  b.book_id,
  b.title,
  b.publishedDate,
  b.authors,
  b.genres,
  COUNT(DISTINCT r.review_id) as review_count,
  AVG(r.rating) as calculated_avg_rating,
  AVG(r.base_sentiment_score) as avg_sentiment,
  APPROX_QUANTILES(r.rating, 100)[OFFSET(50)] as median_rating,
  ARRAY_AGG(DISTINCT r.reviewer_id LIMIT 100) as top_reviewers
FROM `your-project.bookscraperdb.books` b
LEFT JOIN `your-project.bookscraperdb.reviews` r
  ON b.book_id = r.book_id
WHERE b.ingestion_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1,2,3,4,5;

-- Cross-genre analysis (for recommendations)
CREATE MATERIALIZED VIEW `your-project.bookscraperdb.genre_affinity` AS
SELECT 
  g1.genre_name as genre_1,
  g2.genre_name as genre_2,
  COUNT(DISTINCT b.book_id) as shared_books,
  AVG(b.averageRating) as avg_rating,
  COUNT(DISTINCT r.reviewer_id) as shared_readers
FROM `your-project.bookscraperdb.books` b,
     UNNEST(b.genres) as g1,
     UNNEST(b.genres) as g2
LEFT JOIN `your-project.bookscraperdb.reviews` r
  ON b.book_id = r.book_id
WHERE g1 < g2  -- Avoid duplicates
GROUP BY 1,2
HAVING shared_books > 10;