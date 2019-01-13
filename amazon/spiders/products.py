    
import scrapy
from utils import removeSpaceAndStrip, readFile, notif, getCookiesInUS
from amazon.items import AmazonItem
import random
from enum import Enum

class Mode(Enum):
    KEYWORD = 1
    FILE = 2
        

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

    cookies = getCookiesInUS()

    def start_requests(self):
        try:
            file = self.file
            mode = Mode.FILE
        except AttributeError:
            mode = Mode.KEYWORD

        if (mode == Mode.KEYWORD):
            url = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + self.keyword
            yield scrapy.Request(url=url, callback=self.parse, headers={"user-agent": random.choice(self.headers)}, cookies=self.cookies)
            # for url in urls:
            #     yield scrapy.Request(url=url, callback=self.parse, headers={"user-agent": random.choice(self.headers)})
        else:
            # url = self.link
            links = readFile(file)
            for link in links:
                if "http" in link:
                    yield scrapy.Request(url=link, callback=self.parse_product, headers={"user-agent": random.choice(self.headers)}, cookies=self.cookies)
                else:
                    notif("INVALID LINK: " + link)
            # return ######

    def parse(self, response):
        # print(self.number)
        asins = response.xpath("//*[contains(@id, 'result')]/@data-asin").extract()
        for asin in asins:
            url_asin = "https://www.amazon.com/dp/" + asin;
            yield scrapy.Request(url=url_asin, callback=self.parse_product, headers={"user-agent": random.choice(self.headers)}, cookies=self.cookies)
        next_page = response.xpath('//*[@id="pagnNextLink"]/@href').extract_first()
        if (next_page is not None):
            yield response.follow(next_page, callback=self.parse, cookies=self.cookies)

    def parse_product(self, response):
        feature_bullets = response.xpath('//*[@id="feature-bullets"]/ul/li/span')
        temp_short_description = ""
        for feature_bullet in feature_bullets:
            temp_short_description = temp_short_description + removeSpaceAndStrip(feature_bullet.xpath("text()").extract_first()) + " | "
        
        temp_price = response.xpath('//span[@id="priceblock_ourprice"]/text()').extract_first()
        if temp_price is not None:
            if len(temp_price) > 5:
                temp_price = temp_price.split(" - ")[0]
        else:
            temp_price = response.xpath('//*[@id="priceblock_snsprice_Based"]/span/text()').extract_first()
            if temp_price is None:
                temp_price = "can't get"
        # Handle description
        try:
            temp_description = ''
            e_temp_descriptions = response.xpath('//*[@id="productDescription"]/p/text()').extract()
            # other_form_descriptions = response.xpath('//*[contains(@class, "launchpad-text-left-justify"")]/p/text()').extract()
            if len(e_temp_descriptions) >= 2:
                for e_temp_description in e_temp_descriptions:
                    temp_description = temp_description + e_temp_description + "\n"
            elif (len(e_temp_descriptions) == 1):
                temp_description = e_temp_descriptions[0]
            # elif len(other_form_descriptions) > 2:
            else:
                e_temp_descriptions = response.xpath('//*[contains(@class, "launchpad-text-left-justify"")]/p/text()').extract()
                if len(e_temp_descriptions) >= 2:
                    for e_temp_description in e_temp_descriptions:
                        temp_description = temp_description + e_temp_description + "\n"
                else:
                    e_temp_descriptions = response.xpath('//*[contains(@class, "launchpad-text-left-justify"")]/ul/li/span/text()').extract()
                    for e_temp_description in e_temp_descriptions:
                        temp_description = temp_description + e_temp_description + "\n"
            
        except Exception as e:
            temp_description = "Nothing"

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

        self.count+=1
        notif("Success " + response.url.split("/")[-1])
        yield item