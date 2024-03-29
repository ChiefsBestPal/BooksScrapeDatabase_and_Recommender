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

CREATE TABLE GenericBookProfile (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id VARCHAR(10) NOT NULL,
    website_specific_info TEXT,
    comments TEXT,
    reviews TEXT,
    ratings DECIMAL(3, 2),
    genres TEXT,
    topics TEXT,
    keywords TEXT,
    related_works TEXT,
    related_authors TEXT,
    rankings TEXT,
    discussions TEXT,
    articles TEXT,
    prices TEXT,
    popularity_statistics TEXT,
    other_statistics TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES Book(ISBN10)
);

-- TODO: Do IS-A Hierarchy for Types of Books: Magasine, Short stories, Comic Book, Journal, Paper, Novel, etc...ABORT

-- TODO: Do IS-A Hierarchy for APIs of BooksProfiles: Goodreads,GoogleBooks, ISBNdb

-- TODO: Do IS-A Hierarchy for users: Authors, Publisher, Editor, Fan/Follower (depends on API), goodread user, google user, public commenter,




-- TODO ? : GoodReads API user systems ??: Fanship, Bookshelves, favorites, follows, groups, toReadList, friends, etc.... 