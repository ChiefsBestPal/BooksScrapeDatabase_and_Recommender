import csv

# Path to your CSV file
csv_file = 'books_antoine.csv'

# Path to the output text file
output_file = 'book_ids1.txt'

# List to store book IDs
book_ids = []

# Counter for the number of book entries processed
count = 0

MAX_NUM_BOOKS = 3000

# Open the CSV file and read the data
with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['url'].startswith('https://www.goodreads.com/book/show/'):
            book_id = row['url'].split('/')[-1]
            book_ids.append(book_id)
            count += 1
            if count >= MAX_NUM_BOOKS:
                break

# Write book IDs to a text file, 1 ID per line
with open(output_file, 'w') as file:
    file.write('\n'.join(book_ids))

print("Book IDs written to", output_file)