# Books Database(s) Generators and Concurrent Crawlers for litterature data
Since 2024
<img width="1412" height="678" alt="image" src="https://github.com/user-attachments/assets/7b80b8b7-aefd-4287-b927-420496347aa4" />

<img width="1308" height="722" alt="image" src="https://github.com/user-attachments/assets/ef19a897-d30e-4615-b1b4-929fcc415ffa" />

## Maintaining and scaling
____
This project is maintained, improved and reused for mutiple subprojects / personal purposes. \
> That includes but not limited to: New/Updated scraped entries, Parser improvements, DB indexes/constraints, maintenance, benchmark, data integrity, updates, new ratings/reviews models for recommender, ...


Used to be a database project taken much further afterwards for big data analytics, influence networks, similarity profiles, more advanced DDL automation, better normalized schemas, low-level optimizations 


**Copyright 2024-?: Antoine Cantin 'ChiefsBestPal'**
____

## APIs and public data sources:

> https://www.goodreads.com/api (Meaningful for community aspect of sharing, reviewing, commenting etc...)

> https://developers.google.com/books (Go to bulk book data reference API)

> https://openlibrary.org/ (Good with Python integration APIs and scraping)

> https://isbndb.com/ (Great to obtain formal statistics, IDs, etc... of authors, books and collections)

## Special unique features

- SQL DML Code generator for lists,authors, books, reviews
- Goodreads Reviews scrapping
- NoSQL Neo4j optimized data visualizations and analysis
- Use of multiple APIs, all of which's data are cross referenced and combined parsed into clean outputs
- Multi-thread and items pairing abilities for more efficient spiders
- Raw search keywords spider + commands
- Specific probability/statistical models for relevant rating systems to properly profile a reader and make recommendation for it
- Neo4j queries+scripts to identify and learn reading trends, cross-genre factors, authors' influence networks, find niche series/books from complex reviewers patterns

## Original ERD ... Slightly different for "NoSQL schemas"
<img width="1831" height="1743" alt="ERD_DataModel" src="https://github.com/user-attachments/assets/aebcc229-eed6-4317-8ceb-4756f0f416db" />


## Example outputs
### Raw web scrapped files from all spiders
![image](https://github.com/user-attachments/assets/f6675bf6-4c7d-4678-a7d8-7ae874c869f6)
![image](https://github.com/user-attachments/assets/0bb76fb8-385e-4b33-a347-af9ad32e41e9)

> Message personally for access to much more semi-structured and structured data outputs from the main crawling and parsing pipelines.

#### Custom scrapes for Goodreads Reviews (Resource Intensive)
![image](https://github.com/user-attachments/assets/3ff5452c-cdfc-4b6a-be80-9fb3c64624c3)
### SQL DML Code generated, parsed, filtered and formatted from raw scraped data
![image](https://github.com/user-attachments/assets/a9b2b78f-393a-41a6-80b5-95207eb86cea)

# Populating the Database

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
## ```DML_Generators_and_API_Caching\main.py```
This file (780 lines) writes all necessary .txt files that are then pasted directly
into .sql file and queries in a MySQL workbench as is to produce all the necessary 
INSERT dml statements to populate the db.
```DML_Generators_and_API_Caching\generate_network_requests_caches.py``` should only be ran to cache the Googlebooks and OpenLibrary requests. It takes a very long time as it updates/overwrites caches of all needed API requests (caching and datastructures that are hashable are used everywhere because it makes every sql generator and linker algorithms so much faster and much more testable)

```Parsers_And_RawFileDump/``` contains formatters, parsers and raw scrapped/api requested files.


## Code information
> Large codebase (Few thousand lines); First Phase took a week and final generators went through 6 major versions

1. Our 2 APIs (excluding crawled websites) (Google books and Open Library) have 3 total requests per book profile iteration. This can be extremely long and present networking issues so ```All_Scripts\DML_Generators\generate_network_requests_caches.py``` allows one to leave this script running and cache in a spec_dict.json all the necessary requests informations which speeds up the DML generation exponentially and makes our whole operation alongside webscraping, parsing operations and checks much less flaky, much faster and much more reliable / versatile. 

2. Webscrapping has been performed at several levels. Multiple different concurrent spider / crawling techniques were tested, optimized and developped over the course of several days. \
The initial code is inspired and taken from ```https://github.com/havanagrawal/GoodreadsScraper```, but we completely repurposed it and ALSO added enormously onto it by creating different types of crawlers, loaders, networking settings tests and optimizations, etc....
> Crawled and scrapped authors, related authors, books, series and a ton of other information from goodreads lists of readings
> Crawled and scrapped the same things again but from popular reading lists and queues within popular user profiles and posts
> Crawled and scrapped additional necessary author UIDs as well as reviewers and reviewe information which was encoded in special tags in the XML and preloaded scripts
> And more...
```GoodreadsScraper/spiders/...``` to see goodreads crawlers and other crawlers


## Results of first phases

Over the course of several days and nights, over 1 GB of total data was API requested and Webscrapped by several different crawlers on different machines. Caches and data structure optimizations played a huge role in final success and later versions of the codes. <br>

Our information was then formatted, cleaned up, verified and structured into readable csv and json files before being all processed, integrated and linked together in the main.py code to generate necessary MySQL DML code. It is then straight forward to take make CSVs out of the SQL db populated by these DML and make a Neo4j NoSQL Graph database out of said CSVs, using DDL constraints, attributes, indexes the same in neo4j's cypher.




