import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
from pymongo import MongoClient


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

        # Collecting authors information
        authors = response.css('div.quote small.author::text').getall()
        for author in authors:
            author_url = response.urljoin(f"/author/{author.replace(' ', '-')}")
            yield scrapy.Request(author_url, callback=self.parse_author)

    def parse_author(self, response):
        yield {
            'name': response.css('h3.author-title::text').get().strip(),
            'birth_date': response.css('span.author-born-date::text').get(),
            'birth_location': response.css('span.author-born-location::text').get(),
            'description': response.css('div.author-description::text').get().strip(),
        }


def run_spider(spider):
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(spider)
    process.start()


def load_to_mongodb(quotes_file, authors_file, mongo_uri, mongo_db):
    client = MongoClient(mongo_uri)
    db = client[mongo_db]

    with open(quotes_file, 'r') as f:
        quotes = json.load(f)
        if isinstance(quotes, list):
            db.quotes.insert_many(quotes)
        else:
            db.quotes.insert_one(quotes)

    with open(authors_file, 'r') as f:
        authors = json.load(f)
        if isinstance(authors, list):
            db.authors.insert_many(authors)
        else:
            db.authors.insert_one(authors)

    client.close()


if __name__ == "__main__":
    run_spider(QuotesSpider)

    # Завантаження в MongoDB
    MONGO_URI = connect(host="mongodb+srv://yaroslavtarnopil:<password>@cluster0.kqcceae.mongodb.net/")
    MONGO_DB = "quotes_db"

    load_to_mongodb("quotes.json", "authors.json", MONGO_URI, MONGO_DB)
