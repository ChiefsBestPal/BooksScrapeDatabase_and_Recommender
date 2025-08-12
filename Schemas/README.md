# Base DDL of the Database
Provided in SQL, but used to infer after parsing the relationships/schemas for NoSQL DBs
## Populating database

> PLEASE BE CAREFUL THE .txt/.sql FILES HAVE AN ORDER THAT THEY SHOULD BE INSERTED IN DML IN THE DATABASE

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

### ```All_Scripts\DML_Generators\main.py```
This file (780 lines) writes all necessary .txt files that are then pasted directly
into .sql file and queries in a MySQL workbench as is to produce all the necessary 
INSERT dml statements to populate the db.
```generate_network_requests_caches.py``` should only be ran to cache the Googlebooks and OpenLibrary requests. It takes a very long time as it updates/overwrites caches of all needed API requests (caching and datastructures that are hashable are used everywhere because it makes every sql generator and linker algorithms so much faster and much more testable)

```All_Scripts/ScrapedRawFiles_And_ParsersCode``` contains formatters, parsers and raw scrapped/api requested files.


## Code information (Very large codebase, Phase 1 took over a week)

There are many other files. Our code has went through **6 MAJOR VERSIONS** over the course of several days. \

1. Our 2 APIs (Google books and Open Library) have 3 total requests per book profile iteration. This can be extremely long and present networking issues so ```All_Scripts\DML_Generators\generate_network_requests_caches.py``` allows one to leave this script running and cache in a spec_dict.json all the necessary requests informations which speeds up the DML generation exponentially and makes our whole operation alongside webscraping, parsing operations and checks much less flaky, much faster and much more reliable / versatile. 

2. Webscrapping has been performed at several levels. Multiple different concurrent spider / crawling techniques were tested, optimized and developped over the course of several days. \
The initial code is inspired and taken from ```https://github.com/havanagrawal/GoodreadsScraper```, but we completely repurposed it and ALSO added enormously onto it by creating different types of crawlers, loaders, networking settings tests and optimizations, etc....
> Crawled and scrapped authors, related authors, books, series and a ton of other information from goodreads lists of readings
> Crawled and scrapped the same things again but from popular reading lists and queues within popular user profiles and posts
> Crawled and scrapped additional necessary author UIDs as well as reviewers and reviewe information which was encoded in special tags in the XML and preloaded scripts
> And more...
```GoodreadsScraper/spiders/...``` to see goodreads crawlers and other crawlers


## Results

Over the course of several days and nights, over 1 GB of total data was API requested and Webscrapped by several different crawlers on different machines. Caches and data structure optimizations played a huge role in our final success and later versions of the codes. <br>

Our information was then formatted, cleaned up, verified and structured into readable csv and json files before being all processed, integrated and linked together in the main.py code to generate necessary MySQL DML code.


## Other Discussions and more in depth information

**SEE THE PHASE 1 REPORT DOCUMENT**
