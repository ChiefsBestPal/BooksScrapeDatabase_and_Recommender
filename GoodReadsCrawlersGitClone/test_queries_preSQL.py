import json
import csv
import re
import operator as op
from collections import defaultdict

def escapeSQLChars(s : str) -> str: return s.replace("'", "\'").replace("(", "\(").replace(")", "\)")




def parse_string_list(string_list):
    parts = []
    current_part = ""
    in_string = False

    for char in string_list:
        if char == "'":
            in_string = not in_string
            current_part += char
        elif char == "," and not in_string:
            parts.append(current_part.strip())
            current_part = ""
        else:
            current_part += char

    # Add the last part
    parts.append(current_part.strip())

    return parts

string_list = "['ABC',  'DE, 'FG',  'Hello's the names' right']"

print(parse_string_list(string_list))
# Split string considering both commas and single quotes
parts = re.findall(r"'[^']*'|[^,]+", string_list)

# Reconstruct list considering single apostrophes
parsed_list = []
current_string = ''
for part in parts:
    if part.startswith("'") and part.endswith("'"):
        parsed_list.append(part[1:-1])
    else:
        current_string += part.strip()
        if current_string:
            parsed_list.append(current_string)
        current_string = ''

print(parsed_list)

exit()
MODE  = 1

# if MODE == 1:
def normalize_name(name):
    """
    Normalize the author's name by removing spaces, abbreviations, and variations.
    """
    # Convert to lowercase and remove extra spaces
    normalized_name = ' '.join(re.sub(r"\s{2,}"," ",name.strip().lower()).split())
    
    # # Remove common abbreviations
    # normalized_name = re.sub(r'\b(dr|mr|mrs|ms)\.?\b', '', normalized_name)

    # Remove middle initials
    normalized_name = re.sub(r'\b\w\.?\b', '', normalized_name)

    # Split the name into components
    name_components = normalized_name.split()

    # Sort the name components alphabetically
    sorted_components = sorted(name_components)

    # Join the sorted components
    normalized_name = ' '.join(sorted_components)

    return normalized_name

def check_duplicate_names(authors):
    """
    Check for duplicate names among authors.
    """
    # Dictionary to store normalized names and their corresponding counts
    name_counts = defaultdict(list)

    for author in authors:
        #normalized_name = normalize_name(author['name'])
        normalized_name = re.sub(r"\s{2,}"," ",author['name'].strip().lower())
        # Update the count for the normalized name
        #name_counts[normalized_name] = name_counts.get(normalized_name, 0) + 1
        
        name_counts[normalized_name].append(author['url'].removeprefix("https://www.goodreads.com/author/show/"))
    # Find duplicate names
    # duplicate_names = [name for name, count in name_counts.items() if count > 1]

    # return duplicate_names
    return dict(filter(lambda kv: len(kv[1]) >= 2, name_counts.items()))
# Load the CSV file
authors = []
with open('authors_final_antoine.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        authors.append(row)

# Check for duplicate names
duplicate_names_dic = check_duplicate_names(authors)

if duplicate_names_dic and True:
    print("Duplicate names found:")
    for name,uids in duplicate_names_dic.items():
        print(name,end="\n\t")
        print(*uids, sep="\n\t")
        print()
else:
    print("No duplicate names found.")
    
duplicate_names = list(duplicate_names_dic.keys())
# elif MODE == 2:
# Load the JSON file
with open('reviews1_reviewers_output.json', 'r') as f:
    data = json.load(f)

# Filter entries with isAuthor as true
nonauthor_entries = [entry for entry in data if not entry.get('isAuthor', False)]
author_entries = [entry for entry in data if entry.get('isAuthor', False)]

for name in map(lambda entry: re.sub(r"\s{2,}"," ",entry['name'].strip().lower()),author_entries):
    if name in duplicate_names:
        print("AADSAD")
# Find the entry with the highest followersCount
if author_entries and True:
    max_followers_entry = max(author_entries, key=lambda x: x.get('followersCount', 0))
    print("Entry with the highest followersCount among authors with isAuthor as true:")
    print(max_followers_entry)
    min_followers_entry = sorted(author_entries, key=lambda x: x.get('followersCount', 0))
    print("Entry with the lowest followersCount among authors with isAuthor as true:")
    print(min_followers_entry[:10])
    max_followers_entry = max(nonauthor_entries, key=lambda x: x.get('followersCount', 0))
    print("Entry with the highest followersCount among authors with isAuthor as false:")
    print(max_followers_entry)
else:
    print("No entry with isAuthor as true found.")

