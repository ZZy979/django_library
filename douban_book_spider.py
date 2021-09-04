import json
import os
import re
from datetime import datetime

import scrapy
from itemadapter import ItemAdapter


class BookItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    publisher = scrapy.Field()
    publish_date = scrapy.Field()
    price = scrapy.Field()
    isbn = scrapy.Field()
    tag = scrapy.Field()
    introduction = scrapy.Field()


class DoubanBookSpider(scrapy.Spider):
    name = 'douban-book'
    allowed_domains = ['book.douban.com']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
        'DOWNLOAD_DELAY': 20,
        'ITEM_PIPELINES': {'douban_book_spider.JsonWriterPipeline': 0}
    }

    def __init__(self, tag='编程', num_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag = tag
        self.num_pages = int(num_pages)

    def start_requests(self):
        url = 'https://book.douban.com/tag/{}?start={:d}&type=T'
        return [
            scrapy.Request(url.format(self.tag, p * 20), callback=self.parse_list)
            for p in range(self.num_pages)
        ]

    def parse_list(self, response):
        for url in response.css('ul.subject-list > li > div.info > h2 > a::attr(href)').getall():
            yield scrapy.Request(url)

    def parse(self, response, **kwargs):
        book = BookItem(tag=self.tag)
        book['title'] = response.css('#wrapper > h1 > span::text').get().strip()
        info = response.xpath('//div[@id="info"]//text()').getall()
        info = [re.sub(r'\s+', ' ', s) for s in info if not s.isspace()]
        for i, s in enumerate(info):
            if s == ' 作者':
                book['author'] = ''.join(info[i + 2:info.index('出版社:')]).strip()
            elif s == '出版社:':
                book['publisher'] = info[i + 1].strip()
            elif s == '副标题:':
                book['title'] += ' : ' + info[i + 1].strip()
            elif s == '出版年:':
                book['publish_date'] = parse_date(info[i + 1].strip())
            elif s == '定价:':
                book['price'] = re.search(r'\d+(\.\d+)?', info[i + 1]).group(0)
            elif s == 'ISBN:':
                book['isbn'] = info[i + 1].strip()
        book['introduction'] = response.css('div.intro > p:first-child::text').get()
        yield book


def parse_date(date):
    if (m := re.match(r'\d{4}-\d{1,2}-\d{1,2}', date)) is not None:
        return datetime.strptime(m.group(0), '%Y-%m-%d').strftime('%Y-%m-%d')
    elif (m := re.match(r'\d{4}-\d{1,2}', date)) is not None:
        return datetime.strptime(m.group(0), '%Y-%m').strftime('%Y-%m-%d')
    elif (m := re.match(r'\d{4}', date)) is not None:
        return datetime.strptime(m.group(0), '%Y').strftime('%Y-%m-%d')
    return None


class JsonWriterPipeline:

    def open_spider(self, spider):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item

    def close_spider(self, spider):
        with open(os.path.join('data', spider.tag + '.json'), 'w', encoding='utf8') as f:
            json.dump({'RECORDS': self.items}, f, ensure_ascii=False)
