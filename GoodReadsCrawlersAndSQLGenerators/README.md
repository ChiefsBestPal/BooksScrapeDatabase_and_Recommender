## Introduction

Scrapy webscrapping x crawlers project to get data from Goodreads.

## Installation

USE A VIRTUAL ENVIRONMENT !!!! adapt the requirements

## How To Run

### List Crawls


```bash
python3 crawl.py list \
  --list_name="1.Best_Books_Ever" \
  --start_page=1 \
  --end_page=50 \
  --output_file_suffix="best_001_050"
```

The paging approach avoids hitting the Goodreads site too heavily. You should also ideally set the `DOWNLOAD_DELAY` to at least 1 (DEPENDS HEAVILY MY VERSION WILL EMPLOY DIFFERENT CONCURRENT SPIDERS AND MAKE USAGE OF AUTHRHROTTLE ON AND OFF WHEN NEEDED).

Use `python3 crawl.py list --help` for all options and defaults.

### My Books (Shelf) Crawls


```bash
python3 crawl.py my-books \
  --shelf="read" \
  --user_id="50993735-emma-watson"
```

Use `python3 crawl.py my-books --help` for all options and defaults.

## Data Enrichment

### Cleaning and Aggregating

```bash
cat book_*.jl > all_books.jl
cat author_*.jl > all_authors.jl
```


```python
import pandas as pd

all_books = pd.read_json('all_books.jl', lines=True)
all_authors = pd.read_json('all_authors.jl', lines=True)
```

```bash
python3 cleanup.py \
  --filenames best_books_01_50.jl young_adult_01_50.jl \
  --output goodreads.csv
```

### Extracting Kindle Price

```bash
# Install selenium, not included in requirements.txt
pip3 install selenium

# Run the Kindle price populator script
python3 populate_kindle_price.py -f goodreads.csv -o goodreads_with_kindle_price.csv
```

## Data Schema

### Book

| Column  | Description |
|---------|-------------|
| url     | The Goodreads URL |
| title   | The title |
| titleComplete   | The complete title |
| description   | Description of the book. May contain HTML/unicode characters. |
| format   | The format in which this book was published |
| imageUrl | Image URL for the book cover |
| author  | The author (or list of authors if there are multiple) \* |
| asin | The [Amazon Standard Identifier Number](https://en.wikipedia.org/wiki/Amazon_Standard_Identification_Number) for this edition |
| isbn | The [International Standard Book Number](https://en.wikipedia.org/wiki/International_Standard_Book_Number) for this edition |
| isbn13 | The [International Standard Book Number](https://en.wikipedia.org/wiki/International_Standard_Book_Number) for this edition, in ISBN13 format |
| ratingsCount | The number of user ratings |
| reviewsCount | The number of user text reviews |
| avgRating | The average rating (1 - 5) |
| numPages | The total number of pages |
| language | The language for this edition |
| publishDate | The publish date for this edition |
| series | The series of which this novel is a part |
| genres | A list of genres/shelves |
| awards | A list of awards (if any) won by this novel. Each award is a JSON object. |
| characters | An (incomplete) list of characters that occur in this novel |
| places | A list of places (locations) that occur in this novel |
| ratingHistogram | A list that has individual rating counts (5, 4, 3, 2, 1) |
| ~original_publish_year~ | The original year of publication for this novel |

\* Goodreads [distinguishes between authors of the same name](https://www.goodreads.com/help/show/20-separating-authors-with-the-same-name) by introducing additional spaces between their names, so this column should be treated with special consideration during cleaning.

### Author

| Column  | Description |
|---------|-------------|
| url     | The Goodreads URL |
| name    | Name of the author |
| birthDate | The author's birth date |
| deathDate | The author's death date \* |
| genres | A list of genres this author writes about |
| influences | A list of authors who influenced this author |
| avgRating | The average rating of all books by this author |
| reviewsCount | The total number of reviews for all books by this author |
| ratingsCount | The total number of ratings for all books by this author |
| about | A short blurb about this author \*\* |
