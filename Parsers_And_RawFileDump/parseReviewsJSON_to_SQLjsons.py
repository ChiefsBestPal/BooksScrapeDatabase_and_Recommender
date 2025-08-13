import json

scraped_json_name = r"reviews1"
# Load the original JSON data
with open(f'{scraped_json_name}.json', 'r') as f:
    original_data = json.load(f)

# Initialize empty lists for reviews and reviewers
reviews_data = []
reviewers_data = []

REVIEW_KEY = 0
REVIEWER_KEY = 0 
# Iterate through each book
for book in original_data:
    book_id = book['book_id']
    
    # Iterate through each review in the book
    for review in book['reviews']:
        # Extract review data
        review_data = {
            # 'review_id': review['review_id'],
            'rating': review['rating'],
            'text': review['text'],
            'updatedAt': review['updatedAt'],
            'createdAt': review['createdAt'],
            'likeCount': review['likeCount'],
            'book_gid': book_id,  # Link review to book
            'reviewer_gid': review['reviewer']['id']  # Link review to reviewer
        }
        reviews_data.append(review_data)
        
        # Extract reviewer data
        reviewer_data = {
            'reviewer_gid': review['reviewer']['id'],  # Rename 'id' to 'reviewer_id'
            'name': review['reviewer']['name'],
            'followersCount': review['reviewer']['followersCount'],
            'isAuthor': review['reviewer']['isAuthor']
            # Add other reviewer attributes as needed
        }
        reviewers_data.append(reviewer_data)

# Write reviews data to JSON file
with open(f'{scraped_json_name}_reviews_output.json', 'w') as f:
    json.dump(reviews_data, f, indent=2)

# Write reviewers data to JSON file
with open(f'{scraped_json_name}_reviewers_output.json', 'w') as f:
    json.dump(reviewers_data, f, indent=2)
