-- Should be the last DDL file to run...

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
