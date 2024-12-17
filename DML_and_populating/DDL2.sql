CREATE DATABASE bookDB;
USE bookDB;

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





-- Relationships
CREATE TABLE bookgenre (
  bookgenre_id INT AUTO_INCREMENT PRIMARY KEY,
  genre_id INT,
  book_id INT,
  FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE,
  UNIQUE(genre_id, book_id)
);

CREATE TABLE BookSubject (
  booksubject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT,
  book_id INT,
  FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(subject_id, book_id)
);

CREATE TABLE BookPublisher (
  bookpublisher_id INT AUTO_INCREMENT PRIMARY KEY,
  publisher_id INT,
  book_id INT,
  FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(publisher_id,book_id)
);

CREATE TABLE BookCharacter (
  bookcharacter_id INT AUTO_INCREMENT PRIMARY KEY,
  character_id INT,
  book_id INT,
  FOREIGN KEY (character_id) REFERENCES characterr(character_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  UNIQUE(character_id, book_id)
);

CREATE TABLE BookPlace (
  bookplace_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  place_id INT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  FOREIGN KEY (place_id) REFERENCES Place(place_id) ON DELETE CASCADE,
  UNIQUE(book_id, place_id)
);

CREATE TABLE BookSeries (
  bookseries_id INT AUTO_INCREMENT PRIMARY KEY,
  series_id INT,
  book_id INT,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  FOREIGN KEY (series_id) REFERENCES Series(series_id) ON DELETE CASCADE,
  UNIQUE(series_id, book_id)
);

CREATE TABLE BookAuthor (
  bookauthor_id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT,
  book_id INT,
  FOREIGN KEY (author_id) REFERENCES Author(author_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
);

CREATE TABLE BookReview (
  bookreview_id INT AUTO_INCREMENT PRIMARY KEY,
  reviewer_id INT,
  book_id INT,
  rev TEXT,
  created DATETIME,
  updated DATETIME,
  likeCount INT,
  rating FLOAT,
  FOREIGN KEY (reviewer_id) REFERENCES Reviewer(reviewer_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
);





-- Indexes
CREATE INDEX BookGenreIndex ON bookgenre(genre_id, book_id);
CREATE INDEX ThumbnailIndex ON Thumbnail(book_id);
CREATE INDEX BookSubjectIndex ON BookSubject(subject_id, book_id);
CREATE INDEX BookPublisherIndex ON BookPublisher(publisher_id, book_id);
CREATE INDEX BookCharacterIndex ON BookCharacter(character_id, book_id);
CREATE INDEX BookPlaceIndex ON BookPlace(book_id, place_id);
CREATE INDEX BookSeriesIndex ON BookSeries(series_id, book_id);
CREATE INDEX RetailPriceIndex ON RetailPrice(book_id);
CREATE INDEX ListPriceIndex ON ListPrice(book_id);
CREATE INDEX AuthorIndex ON Author(person_id);
CREATE INDEX ReviewerIndex ON Reviewer(reviewer_id);
CREATE INDEX BookAuthorIndex ON BookAuthor(author_id, book_id);
CREATE INDEX BookReviewIndex ON BookReview(reviewer_id, book_id);





-- Views
CREATE VIEW BookSummary AS
SELECT
  b.title AS "Title",
  b.publishedDate AS "Publication Date",
  b.description AS "Description",
  b.isbn_10 AS "ISBN10",
  b.isbn_13 AS "ISBN13",
  b.pageCount AS "Number of Pages",
  b.averageRating AS "Average Rating",
  b.ratingsCount AS "Number of Ratings",
  (SELECT CONCAT(amount, ' ', currencyCode) FROM RetailPrice WHERE book_id = b.book_id) AS "Retail Price",
  (SELECT CONCAT(amount, ' ', currencyCode) FROM ListPrice WHERE book_id = b.book_id) AS "List Price"
FROM Book b;


SELECT * FROM BookSummary;


CREATE VIEW PeopleSummary AS
SELECT
  p.person_id AS "Person ID",
  p.person_name AS "Name",
  CASE WHEN EXISTS (SELECT 1 FROM Author a WHERE a.person_id = p.person_id) THEN 'yes' ELSE 'no' END AS "Is Author?",
  CASE WHEN EXISTS (SELECT 1 FROM Reviewer r WHERE r.person_id = p.person_id) THEN 'yes' ELSE 'no' END AS "Is Reviewer?"
FROM Person p;

SELECT * FROM PeopleSummary;


CREATE VIEW AuthorSummary AS
SELECT
  p.person_name AS "Author Name",
  a.birthDate AS "Birth Date",
  a.deathDate AS "Death Date",
  a.avgRating AS "Average Rating",
  a.reviewsCount AS "Number of Reviews",
  a.ratingsCount AS "Number of Ratings",
  a.about as "About",
  (SELECT COUNT(*) FROM BookAuthor WHERE author_id = a.author_id) AS "Number of Books Written"
FROM Person p
JOIN Author a ON p.person_id = a.person_id;

SELECT * FROM AuthorSummary;


CREATE VIEW ReviewerSummary AS
SELECT
  p.person_name AS "Reviewer Name",
  r.followersCount AS "Number of Followers",
  CASE WHEN (r.isAuthor = True) THEN 'yes' ELSE 'no' END AS "Is Author?",
  (SELECT COUNT(*) FROM BookReview WHERE reviewer_id = r.reviewer_id) AS "Number of Reviews Given"
FROM Person p
JOIN Reviewer r ON p.person_id = r.person_id;

SELECT * FROM ReviewerSummary;





-- Instead of using on delete cascade, we use trigger to maintain referential integrity
DELIMITER //
CREATE TRIGGER delete_book_genre_trigger
AFTER DELETE ON Book
FOR EACH ROW
BEGIN
    -- Deleting records from BookGenre where book_id matches the deleted record's book_id
    DELETE FROM bookgenre WHERE book_id = OLD.book_id;
END;
//
DELIMITER ;

-- Test the trigger by deleting a record from the Book table
DELETE FROM Book WHERE book_id = 1;

-- Check if associated records are deleted from the BookGenre table
SELECT * FROM BookGenre WHERE book_id = 1;