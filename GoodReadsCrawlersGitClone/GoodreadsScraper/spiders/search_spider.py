import scrapy
from urllib.parse import urlencode

from GoodreadsScraper.spiders.book_spider import BookSpider

class SearchSpider(scrapy.Spider):
    """
    A spider that takes a list of titles, runs a Goodreads search, 
    and then follows the first matching result to scrape the book details.
    """
    name = "search_spider"

    def __init__(self, titles_to_search=None, desired_language=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titles_to_search = titles_to_search or []
        self.desired_language = desired_language
        self.start_urls = []

    def start_requests(self):
        """
        For each title in `self.titles_to_search`, we craft a Goodreads search URL
        (the old "search" endpoint, or some pattern). Then yield requests.
        """
        base_url = "https://www.goodreads.com/search?"  # May differ if the site is updated
        for title in self.titles_to_search:
            params = {
                "q": title,
                "search_type": "books"
            }
            search_url = base_url + urlencode(params)
            yield scrapy.Request(url=search_url,
                                 callback=self.parse_search_results,
                                 meta={"original_title": title})

    def parse_search_results(self, response):
        """
        Parse the search result page, find the best match link to "/book/show/<id>",
        follow that link to scrape details using BookSpider logic.
        """
        original_title = response.meta["original_title"]

        # For demonstration, we pick the top result. 
        # Real logic might involve fuzzy matching or checking the 'desired_language' if available.
        first_result = response.css("a.bookTitle::attr(href)").get()  # e.g. "/book/show/12345-something"
        if first_result:
            book_url = response.urljoin(first_result)
            yield scrapy.Request(book_url,
                                 callback=self.parse_book_page,
                                 meta={"original_title": original_title})
        else:
            self.logger.warning(f"No search results found for title: {original_title}")

    def parse_book_page(self, response):
        """
        Re-use the BookSpider logic to parse the actual book page.
        """
        # You could either instantiate BookSpider directly, or just re-use the parse logic if it's purely functional.
        # Let's instantiate BookSpider, then call `parse()`:
        book_spider = BookSpider()
        yield from book_spider.parse(response)
