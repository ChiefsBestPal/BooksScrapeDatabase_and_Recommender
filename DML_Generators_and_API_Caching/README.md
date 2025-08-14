# Scraped+APIs Data to SQL DML Generator

This repository contains two Python scripts designed to process scraped Goodreads data and also external APIs' data to generate SQL Data Manipulation Language (DML) statements for populating a relational database.

## Overview

The scripts transform raw Goodreads data (books, authors, reviewers, reviews) combined with data from Google Books API and Open Library API into normalized SQL INSERT statements for a comprehensive book database.

## Files

### 1. `generate_network_requests_caches.py`
**Purpose**: Data collection and caching script
- Fetches additional book metadata from Google Books API and Open Library API
- Caches API responses to avoid repeated requests
- Handles network errors and rate limiting
- Outputs cached data to JSON file for later processing

### 2. `main.py`
**Purpose**: Main data processing and SQL generation script
- Loads cached API data and scraped Goodreads data
- Processes and normalizes all data sources
- Generates SQL INSERT statements for multiple database tables
- Handles data deduplication and referential integrity

## Data Sources

### Input Files Required

#### CSV Files (Scraped Goodreads Data)
- `books_final_antoine.csv` - Book information from Goodreads
- `authors_final_antoine.csv` - Author information from Goodreads

#### JSON Files (Scraped Goodreads Data)
- `reviewers_final_antoine.json` - Reviewer/user information
- `reviews_final_antoine.json` - Book reviews and ratings
- `authoruids2.json` - Author-to-user ID mappings

#### Cached API Data
- `final_spec_dict_request_cache.json` - Cached responses from Google Books and Open Library APIs
#### Cached general pre-processed data
- `.pkl` files - Cached data about authors and users mostly that doesnt always need to be reprocessed

### External APIs Used
- **Google Books API**: Book metadata, thumbnails, pricing, availability
- **Open Library API**: Additional book data and subject classifications

## Database Schema

The scripts generate SQL for the following tables:

### Core Entity Tables
- `book` - Main book information
- `author` - Author details
- `reviewer` - User/reviewer information  
- `person` - Base person entity (authors and reviewers)

### Classification Tables
- `genre` - Book genres/categories
- `subject` - Book subjects from Open Library
- `publisher` - Publishing companies
- `character` - Book characters
- `place` - Locations mentioned in books
- `series` - Book series information

### Relationship Tables
- `bookauthor` - Book-to-author relationships
- `bookgenre` - Book-to-genre relationships
- `booksubject` - Book-to-subject relationships
- `bookpublisher` - Book-to-publisher relationships
- `bookcharacter` - Book-to-character relationships
- `bookplace` - Book-to-place relationships
- `bookseries` - Book-to-series relationships
- `bookreview` - Book reviews and ratings

### Metadata Tables
- `thumbnail` - Book cover images
- `retailPrice` - Retail pricing information
- `listPrice` - List pricing information

## Usage

### Step 1: Data Collection and Caching
```bash
python generate_network_requests_caches.py
```

**What it does:**
- Reads book data from CSV files
- Makes API calls to Google Books and Open Library for each ISBN
- Caches all API responses in `final_spec_dict_request_cache.json`
- Handles network errors gracefully
- Shows progress with tqdm progress bars

**When to use:**
- When you have new book data to process
- When API cache is missing or outdated
- Before running the main processing script

### Step 2: SQL Generation
```bash
python main.py
```

**What it does:**
- Loads all input data (CSV, JSON, cached API responses)
- Processes and normalizes data from all sources
- Generates SQL INSERT statements for all tables
- Outputs separate `.txt` files for each table
- Handles data deduplication using in-memory caches

**Output files generated:**
- `book.txt`, `author.txt`, `reviewer.txt`, `person.txt`
- `genre.txt`, `subject.txt`, `publisher.txt`, `series.txt`
- `character.txt`, `place.txt`, `thumbnail.txt`
- `retailPrice.txt`, `listPrice.txt`
- All relationship table files (`bookauthor.txt`, etc.)
- `bookreview.txt`

## Key Features

### Data Processing Logic

1. **ISBN-based Matching**: Books are processed using ISBN-13 as the primary key
2. **Deduplication**: Uses set-based caching to avoid duplicate entries
3. **Referential Integrity**: Maintains proper foreign key relationships
4. **NULL Handling**: Converts empty strings and None values to SQL NULL
5. **SQL Injection Prevention**: Escapes single quotes in text data

### Performance Optimizations

- **Caching**: API responses cached to avoid repeated requests
- **Progress Tracking**: Visual progress bars for long-running operations
- **Memory Management**: Uses frozensets for efficient deduplication
- **Batch Processing**: Writes data in batches to text files

### Error Handling

- **Network Errors**: Graceful handling of API timeouts and failures
- **Data Validation**: Skips records with missing required fields
- **SQL Safety**: Escapes special characters and handles NULL values

## Configuration

### Limits and Controls
```python
# In main.py - adjust these limits as needed:
if count > 10000000:  # LIMIT OF BOOKS
if end_now == 1000000000:  # LIMIT OF REVIEWERS
```

### File Paths
Update file paths in both scripts if your data files are located elsewhere:
```python
csv_file1 = 'books_final_antoine.csv'
csv_file2 = 'authors_final_antoine.csv'
json_file1 = 'reviewers_final_antoine.json'
# etc.
```

## Dependencies

```bash
pip install requests tqdm line_profiler
```

- `requests` - HTTP library for API calls
- `tqdm` - Progress bar library
- `line_profiler` - Performance profiling (optional)
- `csv`, `json`, `pickle` - Built-in Python libraries

## Database Integration

After running the scripts, import the generated SQL files into your database:

```sql
-- Example for MySQL/PostgreSQL
SOURCE book.txt;
SOURCE author.txt;
SOURCE person.txt;
-- ... continue for all tables
SOURCE bookreview.txt;
```

**Important**: Load tables in the correct order to respect foreign key constraints:
1. Core entities first (`person`, `book`, `author`, etc.)
2. Classification tables (`genre`, `subject`, etc.)
3. Relationship tables last (`bookauthor`, `bookreview`, etc.)

## Troubleshooting

### Common Issues

1. **API Rate Limiting**: If you hit API limits, the script will continue and skip failed requests
2. **Memory Usage**: Large datasets may require increasing system memory
3. **File Encoding**: Ensure all input files use UTF-8 encoding
4. **Missing Cache**: Run `generate_network_requests_caches.py` first if cache file is missing

### Performance Tips

- Run the caching script overnight for large datasets
- Monitor disk space - output files can be large
- Consider processing data in smaller batches for very large datasets

## Data Flow Diagram
For generic average case with no exceptions.

```
Goodreads CSV Files → data1, data2, data3 (raw processing)
                   ↓
Author Matching → data4 (author-book relationships)
                   ↓
API Calls → cached responses (generate_network_requests_caches.py)
                   ↓
Data Normalization → deduplication caches
                   ↓
SQL Generation → .txt files with INSERT statements
```

This system provides a complete pipeline from raw scraped data to a fully normalized relational database ready for analysis and querying.