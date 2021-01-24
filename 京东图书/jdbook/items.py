# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JdbookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    big_cate = scrapy.Field()
    small_href = scrapy.Field()
    page = scrapy.Field()
    book_url = scrapy.Field()
    book_img = scrapy.Field()
    book_name = scrapy.Field()
    book_publish_house = scrapy.Field()
    small_cate = scrapy.Field()
    book_price = scrapy.Field()
