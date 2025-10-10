-- ----------------------------------------------------------------------------
-- Dimension Tables (No partitioning needed - small lookup tables)
-- ----------------------------------------------------------------------------
CREATE TABLE Genre (
  genre_id INT AUTO_INCREMENT PRIMARY KEY,
  genre_name VARCHAR(255) NOT NULL UNIQUE,
  parent_genre_id INT COMMENT 'For hierarchical genres',
  INDEX idx_parent (parent_genre_id)
) ENGINE=InnoDB;

CREATE TABLE Subject (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_name VARCHAR(255) NOT NULL UNIQUE,
  INDEX idx_subject_name (subject_name(100))
) ENGINE=InnoDB;

CREATE TABLE Publisher (
  publisher_id INT AUTO_INCREMENT PRIMARY KEY,
  publisher_name VARCHAR(255) NOT NULL UNIQUE,
  country VARCHAR(100),
  INDEX idx_publisher_name (publisher_name(100))
) ENGINE=InnoDB;

CREATE TABLE characterr (
  character_id INT AUTO_INCREMENT PRIMARY KEY,
  character_name VARCHAR(255) NOT NULL UNIQUE,
  INDEX idx_character_name (character_name(100))
) ENGINE=InnoDB;

CREATE TABLE Place (
  place_id INT AUTO_INCREMENT PRIMARY KEY,
  place_name VARCHAR(255) NOT NULL UNIQUE,
  country VARCHAR(100),
  INDEX idx_place_name (place_name(100))
) ENGINE=InnoDB;

CREATE TABLE Series (
  series_id INT AUTO_INCREMENT PRIMARY KEY,
  series_name VARCHAR(255) NOT NULL UNIQUE,
  total_books INT DEFAULT 0,
  INDEX idx_series_name (series_name(100))
) ENGINE=InnoDB;
