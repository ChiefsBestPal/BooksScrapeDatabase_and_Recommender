import scrapy

from scrapy.loader import ItemLoader
from scrapy.item import Field, Item
from itemloaders.processors import TakeFirst #from scrapy.loader.processors import TakeFirst


class AuthorUidItem(Item):
    author_url = Field()
    user_gid_url = Field()


class AuthorUidLoader(ItemLoader):
    default_output_processor = TakeFirst()

class GoodreadsAuthorUidSpider(scrapy.Spider):
    name = 'goodreads_authoruid'
    start_urls = []
    
    def __init__(self, *args, **kwargs):
        print("...")
        super(GoodreadsAuthorUidSpider, self).__init__(*args, **kwargs)
        with open(r'C:\Users\Antoine\Desktop\BooksDatabase_SOEN363_Project\GoodReadsCrawlersGitClone\author_ids1.txt', 'r') as file:
            author_ids = [line.strip() for line in file]
            self.start_urls = [f'https://www.goodreads.com/author/show/{author_id}' for author_id in author_ids]
    
    def parse(self, response):
        loader = AuthorUidLoader(item=AuthorUidItem(), response=response)
        loader.add_value('author_url', response.url)
        loader.add_css('user_gid_url', 'link[rel="alternate"][type="application/atom+xml"][title="Bookshelves"]::attr(href)')
        yield loader.load_item()     
    # def start_requests(self):

    #     # if duplicate_mode true in settings.py, ensure seen_urls.txt has most recent caching or is reset need to scrape again same authors
    #     with open(r'C:\Users\Antoine\Desktop\BooksDatabase_SOEN363_Project\GoodReadsCrawlersGitClone\author_ids1.txt', 'r') as f:
    #         author_ids = [line.strip() for line in f]
            
    #         # print(f"len(author_urls): {len(author_urls)}") 

    #     for author_id in author_ids:
    #         url = f'https://www.goodreads.com/author/show/{author_id}'
    #         yield scrapy.Request(url, callback=self.parse)

    # def old_parse(self, response):
    #     user_gid = None
        
    #     # Extract user ID from the first tag
    #     # link_tag_1 = response.xpath('//head/link[@rel="alternate" and @type="application/atom+xml" and @title="Bookshelves"]/@href').get()
    #     #link_tag_1 = response.xpath('//head/link[@title="Bookshelves"]/@href').get()
    #     link_tag_1 = response.css('link[rel="alternate"][type="application/atom+xml"][title="Bookshelves"]::attr(href)').get()
    #     if link_tag_1:
    #         print(link_tag_1)
    #         user_gid = link_tag_1.split('/')[-1]

    #     # else:
    #     #     # If user ID extraction fails, try the second tag
    #     #     if not user_gid:
    #     #         # link_tag_2 = response.xpath('//link[@rel="alternate" and @type="application/atom+xml" and ends-with(@title, "Updates")]/@href').get()
    #     #         #link_tag_2 = response.xpath('//head/link[@rel="alternate" and @type="application/atom+xml" and ends-with(@title, "Updates")]/@href').get()
    #     #         link_tag_2 = response.css('link[rel="alternate"][type="application/atom+xml"][title$="Updates"]::attr(href)').get()
    #     #         print(f"link_tag_2: {link_tag_2}")
    #     #         if link_tag_2:
    #     #             user_gid = link_tag_2.split('/')[-1]
                    
    #     # Yield the user ID if extracted successfully
    #     if user_gid:
    #         yield {
    #             'url' : response.url,
    #             'user_gid': user_gid
    #         }
            
        # # both extraction attempts fail, log an error
        # else: 
        #     self.logger.error('Failed to extract user ID from the page')