
# SYSTEM OVERVIEW
Our system is made up of several entities with attributes that correspond to a book structure.
Each entity can be identified with an auto incremented key. Their relationships with other entities
are also represented. An ISA connection exists in which a person can be either an author or a
reviewer. A reviewer might provide feedback on a book, whereas an author creates it. A book
can have multiple genres, themes, subjects, characters, settings, and pricing. A series may
consist of several books. All of those multi-level properties are shown in separate tables to
demonstrate cardinality and participation constraints, while a single property is represented as
the actual attribute of a book. We also constructed an index table to speed up key lookups in
tables that store an entity's primary key. We created a few views to simplify difficult queries,
encapsulate functionality, and improve security by restricting direct access to the underlying
tables.
# ORIGINAL APPROACH AND CHALLENGES
Our original and overall approach was to request the needed data using 3 APIs. This data would
be parsed and insert scripts would be generated. However there were many challenges faced
when populating the database. At first, we wanted to use the goodreads API because it was well
documented and had a lot of information about books such as users, general book information,
author information, and reviews. Unfortunately, we found out that this API was deprecated and
many of these important data were not available through requests. There were 2 other APIs in
mind, Google Books and Open Library, but these only had information about the book. They had
nothing about users, reviews, nor authors. Nonetheless, these two APIs were chosen because
many other book APIs were either deprecated or a subscription was needed.
Web scraping has been performed at several levels. Multiple different concurrent spider
crawling techniques were tested, optimized and developed over the course of several days. The
initial code is inspired and taken from https://github.com/havanagrawal/GoodreadsScraper, but
we completely repurposed it and ALSO added enormously onto it by creating different types of
crawlers, loaders, networking settings tests and optimizations, etc... Crawled and scrapped
authors, related authors, books, series and a ton of other information from goodreads lists of
readings. Crawled and scrapped the same things again but from popular reading lists and
queues within popular user profiles and posts. Crawled and scrapped additional necessary
author UIDs as well as reviewers and review information which was encoded in special tags in
the XML and preloaded scripts.
Initial challenges with these APIs were finding the appropriate data and linking the needed
columns from both APIs, Google Books and Open Library. Books have a unique identifier called
ISBN13. We made python scripts to make requests for each ISBN13, and with the responses
we parsed it to fit our data model and to generate DML scripts. In addition, at that time many
areas were losing power and internet connection which forced us to restart our requests and
scripts.
An issue we ran into while parsing API responses, we realized that many of the data fields were
either empty or overall missing. To fix this, DDLs were modified so that some attributes were
NULLABLE and the script had to be modified to account for these NULL insert generation.
Some fields were missing in the later ISBNs; we had to rerun our DML generator script many
times, which can consume a ton of time (hours), before finalizing the NULLABLEs.
We also had challenges regarding the script for DML insert generation. Due to the nature of our
entities and relationships, many inserts had to be generated iteratively by ISBN13, which
caused a lot of overhead when making requests to the APIs. This slowed down the generation
significantly (hours). To fix this, we had to cache and optimize the data and script respectively.
Through debugging, we found that the requests to the APIs were the bottleneck of the
operation. To reduce overhead of the script, we cached the request responses so that it only
needed to be run once. This removed the request bottleneck issue. Our insert generators
worked by writing into separate text files for each table. To optimize this, we chose to generate
all insert strings before writing to the files. This reduced costly file i/o operations by avoiding
unnecessary opening and closing of files which in turn reduces waiting time for resources and
lock overheads.

# Design / Data definition details
## ERD LINK
https://drive.google.com/file/d/19EzIZu3Xj0jH6j5SjehjWFdPpWNkaDki/view?usp=sharing \


## Hierarchal order of generation of DML populating files
1. book_dml
2. person_dml
3. reviewer_dml
4. author_dml
5. bookauthor_dml
6. bookreview_dml
7. characterr_dml
8. bookcharacter_dml
9. genre_dml
10. bookgenre_dml
11. place_dml
12. bookplace_dml
13. publisher_dml
14. bookpublisher_dml
15. series_dml
16. bookseries_dml
17. subject_dml
18. booksubject_dml
19. listprice_dml
20. retailprice_dml
21. thumbnail_dml