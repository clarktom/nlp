# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Proj1Item(scrapy.Item):
    question = scrapy.Field()
    answers = scrapy.Field()
    numOfAns = scrapy.Field()
    pass