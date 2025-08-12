CREATE DATABASE LiteratureScrapeDB;
USE LiteratureScrapeDB;

-- Entities
CREATE TABLE Book (
  book_id INT AUTO_INCREMENT PRIMARY KEY,
  volume_id VARCHAR(255) UNIQUE,
  ol_book_id VARCHAR(255) UNIQUE,
  ol_work_id VARCHAR(200) UNIQUE,
  title VARCHAR(255) NOT NULL,
  subtitle VARCHAR(255),
  publishedDate DATE,
  description TEXT,
  isbn_10 VARCHAR(20),
  isbn_13 VARCHAR(20),
  pageCount INT,
  content_version VARCHAR(50),
  viewable_image BOOLEAN,
  viewable_text BOOLEAN,
  averageRating FLOAT,
  ratingsCount INT,
  maturityRating VARCHAR(50),
  language VARCHAR(50),
  previewLink VARCHAR(500),
  infoLink VARCHAR(500),
  pdf_available BOOLEAN,
  epub_available BOOLEAN,
  book_gid VARCHAR(255) UNIQUE
);

CREATE TABLE Genre (
  genre_id INT AUTO_INCREMENT PRIMARY KEY,
  genre_name VARCHAR(255) UNIQUE
);

CREATE TABLE Thumbnail (
  thumbnail_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  link VARCHAR(255),
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(thumbnail_id, book_id, link)
);

CREATE TABLE Subject (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_name VARCHAR(255) UNIQUE
);

CREATE TABLE Publisher (
  publisher_id INT AUTO_INCREMENT PRIMARY KEY,
  publisher_name VARCHAR(255) UNIQUE
);

CREATE TABLE characterr (
  character_id INT AUTO_INCREMENT PRIMARY KEY,
  character_name VARCHAR(255) UNIQUE
);

CREATE TABLE Place (
  place_id INT AUTO_INCREMENT PRIMARY KEY,
  place_name VARCHAR(255) UNIQUE
);

CREATE TABLE Series (
  series_id INT AUTO_INCREMENT PRIMARY KEY,
  series_name VARCHAR(255) UNIQUE
);

CREATE TABLE RetailPrice (
  retailPrice_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  currencyCode VARCHAR(20),
  amount FLOAT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(retailPrice_id, book_id, currencyCode, amount)
);

CREATE TABLE ListPrice (
  listPrice_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT UNIQUE,
  currencyCode VARCHAR(20),
  amount FLOAT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(listprice_id, book_id, currencyCode, amount)
);

CREATE TABLE Person (
  person_id INT AUTO_INCREMENT PRIMARY KEY,
  person_name VARCHAR(255),
  user_gid VARCHAR(255) UNIQUE
);

CREATE TABLE Author (
  author_id INT AUTO_INCREMENT PRIMARY KEY,
  person_id INT UNIQUE,
  birthDate DATE,
  deathDate DATE,
  avgRating FLOAT,
  reviewsCount INT,
  ratingsCount INT,
  about TEXT,
  author_gid VARCHAR(255) UNIQUE,
  FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

CREATE TABLE Reviewer (
  reviewer_id INT AUTO_INCREMENT PRIMARY KEY,
  person_id INT UNIQUE,
  followersCount INT,
  isAuthor BOOLEAN,
  FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

