import scrapy
import json
import datetime
from dateutil.parser import parse as dateutil_parse


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

FIRST_BOOKID_IX = 0

LAST_BOOKID_IX = 3000

class GoodreadsReviewsSpider(scrapy.Spider):
    name = 'goodreads_reviews'
    
    
    def start_requests(self):
        # List of book IDs to scrape reviews from
        with open(r'C:\Users\Antoine\Desktop\BooksDatabase_SOEN363_Project\GoodReadsCrawlersGitClone\book_ids1.txt', 'r') as f:
            book_ids = [line.strip() for line in f][FIRST_BOOKID_IX : LAST_BOOKID_IX]

        for book_id in book_ids:
            url = f'https://www.goodreads.com/book/show/{book_id}'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # Extract JSON data from the HTML content
        json_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if json_data:
            try:
                data = json.loads(json_data)
                reviews = self.extract_reviewers_and_reviews(data)
                yield {
                    'book_id': response.url.split('/')[-1],
                    # 'reviewers': reviewers,
                    'reviews': reviews
                }
            except json.JSONDecodeError:
                self.logger.error('Error parsing JSON data')
        else:
            self.logger.error('JSON data not found')

    def extract_reviewers_and_reviews(self, json_data):
        # Extract reviewers and reviews from JSON data
        # Implement your logic here
        # reviewers = []
        # reviews = []
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
        # DATA['reviewers'].extend(list(reviewers.values()))
        # DATA['reviews'].extend(list(reviews))
        return list(reviews)
        #return ret_reviewers, reviews
