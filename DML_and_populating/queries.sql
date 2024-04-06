-- 1. Basic select with a simple where clause:
SELECT b.title AS "Books with more than 300 pages"
FROM Book AS b
WHERE pageCount >= 300;





-- 2. Basic select with a simple group by clause (with and without having clause):
SELECT Genre.genre_name AS "Genre", COUNT(*) AS count_books
FROM bookgenre
JOIN Genre ON bookgenre.genre_id = Genre.genre_id
GROUP BY Genre.genre_name
HAVING count_books >= 1
ORDER BY count_books DESC;

SELECT Genre.genre_name As "Genre", COUNT(*) AS count_books
FROM bookgenre
JOIN Genre ON bookgenre.genre_id = Genre.genre_id
GROUP BY Genre.genre_name
ORDER BY count_books DESC;





-- 3. A simple join select query using cartesian product and where clause vs. a join query using ON:
SELECT Person.person_name AS "Author Name", Book.title as "Book Title"
FROM Person, Author, Book, BookAuthor
WHERE Person.person_id = Author.person_id 
  AND Author.author_id = BookAuthor.author_id 
  AND BookAuthor.book_id = Book.book_id;

SELECT Person.person_name AS "Author Name", Book.title as "Book Title"
FROM Person
JOIN Author ON Person.person_id = Author.person_id
JOIN BookAuthor ON Author.author_id = BookAuthor.author_id
JOIN Book ON BookAuthor.book_id = Book.book_id;





-- 4. A few queries to demonstrate various join types on the same tables: inner vs. outer (left and right) vs. full join. Use of null values in the database to show the differences is required.

-- Temporarily set some existing person_id values to NULL for demonstration
UPDATE Author 
SET person_id = NULL 
WHERE author_id = 1;

UPDATE Author 
SET person_id = NULL 
WHERE author_id = 2;

UPDATE Author 
SET person_id = NULL 
WHERE author_id = 3;

-- Inner Join
SELECT p.person_id, a.author_id
FROM Person AS p
INNER JOIN Author AS a ON p.person_id = a.person_id;

-- Right Outer Join
SELECT p.person_id, a.author_id
FROM Person AS p
LEFT OUTER JOIN Author AS a ON p.person_id = a.person_id;

-- Left Outer Join
SELECT p.person_id, a.author_id
FROM Person AS p
RIGHT OUTER JOIN Author AS a ON p.person_id = a.person_id;

-- Full Outer Join (Simulated using Left and Right Outer Joins)
SELECT p.person_id, a.author_id
FROM Person AS p
LEFT OUTER JOIN Author AS a ON p.person_id = a.person_id
UNION
SELECT p.person_id, a.author_id
FROM Person AS p
RIGHT OUTER JOIN Author AS a ON p.person_id = a.person_id
WHERE p.person_id IS NULL OR a.author_id IS NULL;





-- 5. A couple of examples to demonstrate correlated queries.
-- Find books with at least one reviewer who has more than 200 followers
SELECT b.title as "Book Title"
FROM Book b
WHERE EXISTS (
  SELECT 1
  FROM Reviewer r
  JOIN BookReview br ON r.reviewer_id = br.reviewer_id
  WHERE br.book_id = b.book_id
  AND r.followersCount > 200
);

-- List books with a retail price greater than the average retail price across all books:
SELECT b.title
FROM Book b
WHERE (
  SELECT amount
  FROM RetailPrice rp
  WHERE rp.book_id = b.book_id
) > (
  SELECT AVG(amount)
  FROM RetailPrice
);





-- 6. One example per set operations: intersect, union, and diFFerence vs. their equivalences without using set operations.
-- INTERSECT

SELECT * FROM Book WHERE language = 'English'
INTERSECT
SELECT * FROM Book WHERE subtitle is NULL;

SELECT * FROM Book WHERE language = 'English' AND subtitle is NULL;

-- UNION
SELECT * FROM Book WHERE language = 'English'
UNION
SELECT * FROM Book WHERE subtitle is NULL;

SELECT * FROM Book WHERE language = 'English' OR subtitle is NULL;

-- EXCEPT
SELECT * FROM Book WHERE language = 'English'
EXCEPT
SELECT * FROM Book WHERE subtitle is NULL;

SELECT * FROM Book WHERE language = 'English' AND subtitle is NULL;





-- 7. An example of a view that has a hard-coded criteria, by which the content of the view may change upon changing the hard-coded value (see L09 slide 24).
CREATE VIEW Review_For_Book_ID_2 AS
(SELECT * FROM BookReview WHERE book_id="2");





-- 8. Two implementations of the division operator using a) a regular nested query using NOT IN and b) a correlated nested query using NOT EXISTS and EXCEPT (See [4]).
--  Retrieve titles of books that are not categorized under the genres 'Fiction' or 'Romance'
SELECT b1.title as "Book that are not categorized under the genres 'Fiction' or 'Romance'" FROM Book AS b1
WHERE b1.title NOT IN (
  SELECT b2.title
  FROM Book AS b2
  INNER JOIN bookgenre AS bg ON b2.book_id = bg.book_id
  INNER JOIN Genre AS g ON bg.genre_id = g.genre_id
  WHERE g.genre_name IN ('Fiction', 'Romance')
);

--  Retrieve titles of books that are categorized under the all genres
SELECT DISTINCT b.title as "Retrieve titles of books that are categorized under the all genres"
FROM Book b
WHERE NOT EXISTS (
    SELECT g.genre_id
    FROM Genre g
    EXCEPT
    SELECT bg.genre_id
    FROM bookgenre bg
    WHERE bg.book_id = b.book_id
);





-- 9. Provide queries that demonstrates the overlap and covering constraints.

-- *** DONT FORGET RERUN DATA POPULATION SINCE WE SET person_id IN AUTHOR TO NULL IN QUESTION 4 ***

-- Persons who are both authors and reviewers:
SELECT p.person_name as "Both Author and Reviewer"
FROM Person p
JOIN Author a ON p.person_id = a.person_id
JOIN Reviewer r ON p.person_id = r.person_id;

-- Authors not in Person table
SELECT p.person_name as "Author who isn't a person"
FROM Author a
LEFT OUTER JOIN Person p ON a.person_id = p.person_id
WHERE p.person_id IS NULL;

-- Reviewers not in Person table
SELECT p.person_name as "Reviewer who isn't a person"
FROM Reviewer r
LEFT OUTER JOIN Person p ON r.person_id = p.person_id
WHERE p.person_id IS NULL;