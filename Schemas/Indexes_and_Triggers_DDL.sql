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