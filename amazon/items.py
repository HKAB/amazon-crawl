# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    Identifier = scrapy.Field()
    Type = scrapy.Field()
    SKU = scrapy.Field()
    Name = scrapy.Field()
    Published = scrapy.Field()
    IsFeatured = scrapy.Field()
    VisibilityInCatalogue = scrapy.Field()
    ShortDescription = scrapy.Field()
    Description = scrapy.Field()
    TaxStatus = scrapy.Field()
    InStock = scrapy.Field()
    AllowCustomerReviews = scrapy.Field()
    Price = scrapy.Field()
    Categories = scrapy.Field()
    Tags = scrapy.Field()
    Images = scrapy.Field()
    ExternalURL = scrapy.Field()
    Position = scrapy.Field()
