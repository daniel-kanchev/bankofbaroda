import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankofbaroda.items import Article


class BarodaSpider(scrapy.Spider):
    name = 'baroda'
    start_urls = ['https://www.bankofbarodauk.com/news.htm']

    def parse(self, response):
        links = response.xpath('//div[@class="thumbTitle"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        if 'pdf' in response.url:
            return

        title = response.xpath('//h2[@class="newsDTitle darkColor"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="newsDate"]//text()[2]').get()
        if date:
            date = datetime.strptime(date.strip(), '%B %d, %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="newsDetailRow cf"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
