-- TODO: Once all the entity relationships and entity types are established, 
--        replace appropriately inside website/API specific or context specific tables/entities

CREATE TABLE Book (
    ISBN10 VARCHAR(10) PRIMARY KEY,
    ISBN13 VARCHAR(13) UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publication_date DATE,
    publisher VARCHAR(255),
    binding VARCHAR(50),
    pages INT,
    list_price DECIMAL(10, 2),
    cover_image VARCHAR(255),
    language VARCHAR(50),
    edition VARCHAR(50),
    format VARCHAR(50),
    synopsis TEXT,
    dimensions VARCHAR(50),
    overview TEXT,
    dewey_decimal VARCHAR(20),
    weight DECIMAL(10, 2),
    subject VARCHAR(255),
    
    --TODO series_id INT FOREIGN KEY of Series table
    --TODO num_in_serie INT FOREIGN KEY OF BookSeries table
    --TODO UNIQUE(series_id,num_in_serie)
);

-- TODO: Once all the entity relationships and entity types are established, 
--        replace appropriately inside website/API specific or context specific tables/entities
