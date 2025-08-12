-- Run after Entities are defined

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
