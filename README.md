# Books Database(s) Generators and Concurrent Crawlers for litterature data
Since 2024
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
- Use of multiple APIs, all of which's data are cross referenced and combined parsed into clean outputs
- Multi-thread and items pairing abilities for more efficient spiders
- Raw search keywords spider + commands

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





