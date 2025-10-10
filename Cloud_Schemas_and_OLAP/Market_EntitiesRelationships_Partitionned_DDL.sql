-- ----------------------------------------------------------------------------
-- Price Tables (Partitioned by currency for multi-region support)
-- NB: Region is not always indicated by BookPlace
--      most other tables are bibliographic data/metdata and info about books... 
--      e.g. Book may have characters and historical context or review tags within USA, Georgia... 
--           but that doesnt mean retailer, author, publishers, labeling, supply chain was in USA !
--      Favor authoritative metadata or user profile data for geographic date.
-- ----------------------------------------------------------------------------
CREATE TABLE RetailPrice (
  retailPrice_id BIGINT AUTO_INCREMENT,
  book_id BIGINT NOT NULL,
  currencyCode VARCHAR(3) NOT NULL,  -- ISO 4217 (USD, EUR, GBP)
  amount DECIMAL(10,2),
  price_date DATE DEFAULT (CURRENT_DATE),
  
  PRIMARY KEY (retailPrice_id, currencyCode),
  UNIQUE KEY idx_book_currency (book_id, currencyCode),
  INDEX idx_amount (amount),
  
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
)
ENGINE=InnoDB
PARTITION BY LIST COLUMNS(currencyCode) (
  PARTITION p_usd VALUES IN ('USD'),
  PARTITION p_eur VALUES IN ('EUR'),
  PARTITION p_gbp VALUES IN ('GBP'),
  PARTITION p_other VALUES IN (DEFAULT)
);

CREATE TABLE ListPrice (
  listPrice_id BIGINT AUTO_INCREMENT,
  book_id BIGINT NOT NULL,
  currencyCode VARCHAR(3) NOT NULL,
  amount DECIMAL(10,2),
  
  PRIMARY KEY (listPrice_id, currencyCode),
  UNIQUE KEY idx_book_currency (book_id, currencyCode),
  
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
)
ENGINE=InnoDB
PARTITION BY LIST COLUMNS(currencyCode) (
  PARTITION p_usd VALUES IN ('USD'),
  PARTITION p_eur VALUES IN ('EUR'),
  PARTITION p_gbp VALUES IN ('GBP'),
  PARTITION p_other VALUES IN (DEFAULT)
);

-- ----------------------------------------------------------------------------
-- Thumbnail (Small table, no partitioning)
-- TODO: Add supply chain, Catalog, publisher/multi-label tables or attributes to make this much more useful than it seems currently !
-- ----------------------------------------------------------------------------
CREATE TABLE Thumbnail (
  thumbnail_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  book_id BIGINT NOT NULL,
  link VARCHAR(500),
  size ENUM('small', 'medium', 'large') DEFAULT 'medium',
  
  UNIQUE KEY idx_book_link (book_id, link(255)),
  INDEX idx_size (size),
  
  FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB;