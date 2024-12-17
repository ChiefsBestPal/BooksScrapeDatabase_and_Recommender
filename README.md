# BooksDatabase_SOEN363_Project
Antoine Cantin 2024-2025
## Maintaining and subprojects outside class
____
Initially, meant for final project of SOEN363 Databases class. \
But most features/logic of the project (especially scraping-wise) were a little overkill/were more comprehensive then needed for class 

> Thus this project is maintained, improved and reused for mutiple subprojects / personal purposes. \
**Lead designer, Main coder, Maintainer: Antoine Cantin 'ChiefsBestPal'**
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

## Example outputs
### Raw web scrapped files from all spiders
![image](https://github.com/user-attachments/assets/f6675bf6-4c7d-4678-a7d8-7ae874c869f6)
![image](https://github.com/user-attachments/assets/0bb76fb8-385e-4b33-a347-af9ad32e41e9)
#### Custom scrapes for Goodreads Reviews (Resource Intensive)
![image](https://github.com/user-attachments/assets/3ff5452c-cdfc-4b6a-be80-9fb3c64624c3)
### SQL DML Code generated, parsed, filtered and formatted from raw scraped data
![image](https://github.com/user-attachments/assets/a9b2b78f-393a-41a6-80b5-95207eb86cea)
