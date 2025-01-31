import json
from dateutil.parser import parse as dateutil_parse
import datetime
import requests

def safe_parse_date(input_date):
    try:
        date = datetime.datetime.fromtimestamp(input_date / 1000)
        date = date.strftime("%Y-%m-%d %H:%M:%S")

    except (ValueError,TypeError):
        try:
            date = dateutil_parse(input_date, fuzzy=True, default=datetime.datetime.min)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            date = None
            
    return date

DATA = {'reviewers' : [], 'reviews': [] }


def add_reviewers_and_reviews(json_data):
    global DATA
    
    # print(json.dumps(json_data.get('props', {}).get('pageProps', {}).get('apolloState', {}), indent=4))
    # json_data = json.loads(json_response_text)
    reviewers = {}
    reviews = []

    apollo_state = json_data.get('props', {}).get('pageProps', {}).get('apolloState', {})
    for key, value in apollo_state.items():
        if key.startswith('User:'):
            reviewer_id = key.split(':')[1]
            reviewers[reviewer_id] = {
                'name': value.get('name'),
                'id': reviewer_id,
                'followersCount': value.get('followersCount'),
                'isAuthor': value.get('isAuthor')
            }

    # Extract review information
    for key, value in apollo_state.items():
        if key.startswith('Review:'):
            review = {
                'updatedAt': safe_parse_date(value.get('updatedAt')),
                'createdAt': safe_parse_date(value.get('createdAt')),
                'text': value.get('text'),
                'rating': value.get('rating'),
                'likeCount': value.get('likeCount')
            }
            reviewer_id = value.get('creator', '').get('__ref', '').split(':')[-1]
            review['reviewer'] = reviewers.get(reviewer_id, {})
            reviews.append(review)
    DATA['reviewers'].extend(list(reviewers.values()))
    DATA['reviews'].extend(list(reviews))
     

def html_request_for_reviews(book_id):
    global DATA
    url = f'https://www.goodreads.com/book/show/{book_id}'
    
    try:
        # Send a GET request to the book profile page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
        
        # Extract HTML content from the response
        html_content = response.text
        
        # Extract JSON data from the HTML content
        start_tag = '<script id="__NEXT_DATA__" type="application/json">'
        end_tag = '</script>'
        start_index = html_content.find(start_tag)
        end_index = html_content.find(end_tag, start_index)
        json_data = html_content[start_index + len(start_tag):end_index]

        # Parse the JSON data
        json_dict = json.loads(json_data)
        
        # Call add_reviewers_and_reviews to process the JSON data
        add_reviewers_and_reviews(json_dict)
        
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing JSON data: {e}")

if __name__ == '__main__':
    
    book_id = "2526.Blindness"
    
    html_request_for_reviews(book_id)

    review_output_folder = r"C:\Users\Antoine\Desktop\BooksDatabase_SOEN363_Project\GoodReadsCrawlersGitClone\reviews_result"
    
    with open(review_output_folder + f"\\{book_id}.json", 'w', encoding='utf-8') as f:
        json.dump({ 'reviews': DATA['reviews']}, f, indent=4)#'reviewers': DATA['reviewers'],
        
exit()
with open(r"C:\Users\Antoine\Desktop\BooksDatabase_SOEN363_Project\GoodReadsCrawlersGitClone\test_script_tag.json", 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
add_reviewers_and_reviews(json_data)

print(len(DATA['reviewers']))
print(len(DATA['reviews']))

for reviewer in DATA['reviewers']:
    
    print(json.dumps(reviewer, indent=4))

print("\n\n\n=================================\n\n",end="\n")

for review in DATA['reviews']:
    
    print(json.dumps(review, indent=4))