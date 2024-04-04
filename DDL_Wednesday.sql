-- Using MySQL

CREATE DATABASE myDB;

USE myDB;

-- Used
CREATE TABLE Book (
  book_id INT AUTO_INCREMENT PRIMARY KEY,
  volume_id VARCHAR(255) UNIQUE,
  ol_book_id VARCHAR(255) UNIQUE,
  ol_work_id VARCHAR(200) UNIQUE,
  title VARCHAR(255) NOT NULL,
  subtitle VARCHAR(255),
  publishedDate DATE,
  description TEXT,
  isbn_10 VARCHAR(10),
  isbn_13 VARCHAR(13),
  pageCount INT,
  content_version VARCHAR(50),
  viewable_image VARCHAR(355),
  viewable_text TEXT,
  averageRating FLOAT,
  ratingsCount INT,
  maturityRating VARCHAR(50),
  language VARCHAR(50),
  previewLink VARCHAR(500),
  infoLink VARCHAR(500),
  pdf_available BOOLEAN,
  epub_available BOOLEAN
);

-- Used
CREATE TABLE Genre (
  genre_id INT AUTO_INCREMENT PRIMARY KEY,
  genre_name VARCHAR(255) UNIQUE
);

-- Used
CREATE TABLE Book_Genre (
  bookgenre_id INT AUTO_INCREMENT PRIMARY KEY,
  genre_id INT,
  book_id INT,
  FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(genre_id, book_id)
);

-- Used
CREATE TABLE Thumbnail (
  thumbnail_id AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  link VARCHAR(255),
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(thumbnail_id, book_id, link)
);

-- Used
CREATE TABLE Subject (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_name VARCHAR(255) UNIQUE
);

-- Used
CREATE TABLE Book_Subject (
  booksubject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT,
  book_id INT,
  FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(subject_id, book_id)
);

-- Used
CREATE TABLE Publisher (
  publisher_id INT AUTO_INCREMENT PRIMARY KEY,
  publisher_name VARCHAR(255) UNIQUE
);

-- Used
CREATE TABLE Book_Publisher (
  bookpublisher_id INT AUTO_INCREMENT PRIMARY KEY,
  publisher_id INT,
  book_id INT,
  FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(publisher_id,book_id)
);

-- Used
CREATE TABLE Character (
  character_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) UNIQUE
);

-- Used
CREATE TABLE Book_Character (
  bookcharacter_id INT AUTO_INCREMENT PRIMARY KEY,
  character_id INT,
  book_id INT,
  FOREIGN KEY (character_id) REFERENCES Character(character_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(character_id, book_id)
);

-- Used
CREATE TABLE Place (
  place_id INT AUTO_INCREMENT PRIMARY KEY,
  place_name VARCHAR(255) UNIQUE
);

-- Used
CREATE TABLE Book_Place (
  bookplace_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  place_id INT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  FOREIGN KEY (place_id) REFERENCES Place(place_id) ON DELETE CASCADE,
  UNIQUE(book_id, setting_id)
);

-- Used
CREATE TABLE Series (
  series_id INT AUTO_INCREMENT PRIMARY KEY,
  serie VARCHAR(255) UNIQUE
);

-- Used
CREATE TABLE Book_Series (
  bookseries_id INT AUTO_INCREMENT PRIMARY KEY,
  series_id INT,
  book_id INT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  FOREIGN KEY (series_id) REFERENCES Series(series_id) ON DELETE CASCADE,
  UNIQUE(series_id, book_id)
);

-- Used
CREATE TABLE Retail_Price (
  retailPrice_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  currencyCode VARCHAR(20),
  amount FLOAT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(retailPrice_id, book_id, currencyCode, amount)
);

-- Used
CREATE TABLE List_Price (
  listPrice_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  currencyCode VARCHAR(20),
  amount FLOAT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(listPrice_id, book_id, currencyCode, amount)
);

-- Used
CREATE TABLE Person (
  person_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255)
);

-- Used
CREATE TABLE Author (
  author_id INT AUTO_INCREMENT PRIMARY KEY,
  person_id INT UNIQUE,
  birthDate DATE,
  deathDate DATE,
  avgRating FLOAT,
  reviewsCount INT,
  ratingsCount INT,
  about TEXT,
  FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

-- Used
CREATE TABLE Reviewer (
  reviewer_id INT AUTO_INCREMENT PRIMARY KEY,
  person_id INT UNIQUE,
  username VARCHAR(255) UNIQUE,
  reviewCount INT,
  ratingsCount INT,
  avgRating FLOAT,
  detail TEXT,
  FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

-- Used
CREATE TABLE Book_Author (
  bookauthor_id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT,
  book_id INT,
  FOREIGN KEY (author_id) REFERENCES Author(author_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
);

-- Used
CREATE TABLE Book_Reviewer (
  bookreviewer_id INT AUTO_INCREMENT PRIMARY KEY,
  reviewer_id INT,
  book_id INT,
  FOREIGN KEY (reviewer_id) REFERENCES Reviewer(reviewer_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
);

