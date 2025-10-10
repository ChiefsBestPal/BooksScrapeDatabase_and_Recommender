-- ----------------------------------------------------------------------------
-- Junction Tables (With basic composite indexes, adjust to requirements)
-- Base Graph NoSQL compat note: If dimensions/entities are NDOES of GraphDB/GDS, then these are the Core EDGES defintions
-- Tune stored data types/resources and index types in Graph DB according to your main Big Data analytics needs
-- ----------------------------------------------------------------------------
CREATE TABLE BookGenre (
  bookgenre_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  genre_id INT NOT NULL,
  book_id BIGINT NOT NULL,
  
  UNIQUE KEY idx_genre_book (genre_id, book_id),
  INDEX idx_book_genre (book_id, genre_id),  -- Reverse index for queries
  
  FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE BookAuthor (
  bookauthor_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  author_id BIGINT NOT NULL,
  book_id BIGINT NOT NULL,
  author_role VARCHAR(50) DEFAULT 'author' COMMENT 'author, co-author, editor',
  
  UNIQUE KEY idx_author_book (author_id, book_id),
  INDEX idx_book_author (book_id, author_id),
  
  FOREIGN KEY (author_id) REFERENCES Author(author_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE BookSubject (
  booksubject_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL,
  book_id BIGINT NOT NULL,
  
  UNIQUE KEY idx_subject_book (subject_id, book_id),
  INDEX idx_book_subject (book_id, subject_id),
  
  FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE BookPublisher (
  bookpublisher_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  publisher_id INT NOT NULL,
  book_id BIGINT NOT NULL,
  
  UNIQUE KEY idx_publisher_book (publisher_id, book_id),
  INDEX idx_book_publisher (book_id, publisher_id),
  
  FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE BookCharacter (
  bookcharacter_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  character_id INT NOT NULL,
  book_id BIGINT NOT NULL,
  
  UNIQUE KEY idx_character_book (character_id, book_id),
  INDEX idx_book_character (book_id, character_id),
  
  FOREIGN KEY (character_id) REFERENCES characterr(character_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE BookPlace (
  bookplace_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  book_id BIGINT NOT NULL,
  place_id INT NOT NULL,
  
  UNIQUE KEY idx_book_place (book_id, place_id),
  INDEX idx_place_book (place_id, book_id),
  
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  FOREIGN KEY (place_id) REFERENCES Place(place_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE BookSeries (
  bookseries_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  series_id INT NOT NULL,
  book_id BIGINT NOT NULL,
  position_in_series INT COMMENT 'Book 1, Book 2, etc.',
  
  UNIQUE KEY idx_series_book (series_id, book_id),
  INDEX idx_book_series (book_id, series_id),
  INDEX idx_series_position (series_id, position_in_series),
  
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
  FOREIGN KEY (series_id) REFERENCES Series(series_id) ON DELETE CASCADE
) ENGINE=InnoDB;