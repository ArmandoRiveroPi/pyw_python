import scrapy
from scrapy.http import Response





class PywSpider(scrapy.Spider):
    name = 'pyw_spider'
    allowed_domains = ['proveyourworth.com']
    start_urls = ['https://proveyourworth.com/test3']

    custom_settings = {
        'ROBOTSTXT_OBEY': 'False',
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        },
    }


    def parse(self, response: Response):
        print(response.body)
