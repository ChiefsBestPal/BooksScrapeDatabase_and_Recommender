import csv

# Path to your CSV file
csv_file = 'authors_final_antoine.csv'

# Path to the output text file
output_file = 'author_ids1.txt'

# List to store author IDs
author_ids = []

# Counter for the number of author entries processed
count = 0

MAX_NUM_AUTHORS = 12000

# Open the CSV file and read the data
with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['url'].startswith('https://www.goodreads.com/author/show/'):
            author_id = row['url'].split('/')[-1]
            author_ids.append(author_id)
            count += 1
            if count >= MAX_NUM_AUTHORS:
                break

# Write author IDs to a text file, 1 ID per line
with open(output_file, 'w') as file:
    file.write('\n'.join(author_ids))

print("Author IDs written to", output_file)
