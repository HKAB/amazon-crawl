
import scrapy
from utils import removeSpaceAndStrip
from amazon.items import AmazonItem
import random

class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    count = 0

    headers = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    ]

    def start_requests(self):
        if self.link == "":
            url = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + self.keyword
            scrapy.Request(url=url, callback=self.parse, headers={"user-agent": random.choice(self.headers)})
            print("headers: " + self.headers)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse, headers={"user-agent": random.choice(self.headers)})
        else:
            url = self.link
            yield scrapy.Request(url=url, callback=self.parse_product, headers={"user-agent": random.choice(self.headers)})
            # return ######

    def parse(self, response):
        asins = response.xpath("//*[contains(@id, 'result')]/@data-asin")
        for asin in asins:
            if (self.count < self.number):
                url_asin = "https://www.amazon.com/dp/" + asin;
                yield scrapy.Request(url=url_asin, callback=self.parse_product, headers={"user-agent": random.choice(self.headers)})
            else:
                break
        next_page = response.xpath('//*[@id="pagnNextLink"]').extract_first()
        if (next_page is not None) and (self.count < self.number):
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        if (self.count < self.number):
            feature_bullets = response.xpath('//*[@id="feature-bullets"]/ul/li/span')
            print(feature_bullets)
            temp_short_description = ""
            for feature_bullet in feature_bullets:
                temp_short_description = temp_short_description + removeSpaceAndStrip(feature_bullet.xpath("text()").extract_first()) + " | "
            
            temp_price = response.xpath('//*[@id="priceblock_ourprice"]/text()').extract_first()
            if len(temp_price) > 5:
                temp_price = temp_price.split(" - ")[0]

            try:
                temp_description = removeSpaceAndStrip(response.xpath('//*[@id="productDescription"]/p/text()').extract_first())
            except Exception as e:
                temp_description = ""

            item = AmazonItem()
            item["Identifier"] = self.count
            item["Type"] = "external"
            item["SKU"] = response.url.split("/")[-1]
            item["Name"] = response.xpath('//*[@id="productTitle"]/text()').extract_first().strip()
            item["Published"] = "1"
            item["IsFeatured"] = "0"
            item["VisibilityInCatalogue"] = "visible"
            item["ShortDescription"] = temp_short_description
            item["Description"] = temp_description
            item["TaxStatus"] = "taxable"
            item["InStock"] = "100"
            item["AllowCustomerReviews"] = "1"
            item["Price"] = temp_price
            item["Categories"] = "Fashion"
            item["Tags"] = ""
            item["Images"] = response.xpath('//*[@id="landingImage"]/@data-old-hires').extract_first()
            item["ExternalURL"] = "https://www.amazon.com/dp/" + response.url.split("/")[-1] + "?tag=vttgreat-20"
            item["Position"] = "0"

            yield item
        else:
            yield