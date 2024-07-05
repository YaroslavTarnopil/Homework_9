import scrapy
import json

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        quotes = response.css('div.quote')
        for quote in quotes:
            text = quote.css('span.text::text').get()
            author = quote.css('small.author::text').get()
            tags = quote.css('div.tags a.tag::text').getall()

            yield {
                'text': text,
                'author': author,
                'tags': tags
            }

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        
        # Collecting authors information
        authors = response.css('div.quote small.author::text').getall()
        for author in authors:
            author_url = response.urljoin(f"/author/{author.replace(' ', '-')}")
            yield scrapy.Request(author_url, callback=self.parse_author)

    def parse_author(self, response):
        name = response.css('h3.author-title::text').get().strip()
        birth_date = response.css('span.author-born-date::text').get()
        birth_location = response.css('span.author-born-location::text').get()
        description = response.css('div.author-description::text').get().strip()

        yield {
            'name': name,
            'birth_date': birth_date,
            'birth_location': birth_location,
            'description': description
        }
