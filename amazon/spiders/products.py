    
import scrapy
from utils import removeSpaceAndStrip, readFile, notif, getCookiesInUS, printableString
from amazon.items import AmazonItem
import random
from enum import Enum

class Mode(Enum):
    KEYWORD = 1
    FILE = 2
        

class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    count = 0
    count_fail = 0

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

        header = random.choice(self.headers)

        if (mode == Mode.KEYWORD):
            url = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + self.keyword
            yield scrapy.Request(url=url, callback=self.parse, headers={"user-agent": header}, cookies=self.cookies)
        else:
            links = readFile(file)
            notif(header)
            header = random.choice(self.headers)
            for link in links:
                if "http" in link:
                    yield scrapy.Request(url=link, callback=self.parse_product, headers={"user-agent": header}, cookies=self.cookies)
                else:
                    notif("INVALID LINK: " + link)

    def parse(self, response):
        asins = response.xpath("//*[contains(@id, 'result')]/@data-asin").extract()
        for asin in asins:
            notif(asin)
            url_asin = "https://www.amazon.com/dp/" + asin;
            yield scrapy.Request(url=url_asin, callback=self.parse_product, headers={"user-agent": random.choice(self.headers)}, cookies=self.cookies)
        next_page = response.xpath('//*[@id="pagnNextLink"]/@href').extract_first()
        if (next_page is not None):
            header = random.choice(self.headers)
            yield response.follow(next_page, callback=self.parse, cookies=self.cookies, headers={"user-agent": header})

    def parse_product(self, response):
        captcha = response.xpath('//*[@id="captchacharacters"]').extract_first()
        if response.status == 404:
            print("404")
            item = AmazonItem()
            item["Identifier"] = self.count_fail
            item["Name"] = "404 Not Found"
            item["ExternalURL"] = response.url
            self.count_fail += 1
            yield item
        elif (captcha is None):
            temp_title = response.xpath('//*[@id="productTitle"]/text()').extract_first()
            if temp_title is not None:
                temp_title = removeSpaceAndStrip(printableString(temp_title))

            # Handle description
            temp_short_description = response.xpath('//*[@id="feature-bullets"]//*  ').extract_first()

            # Handle price
            temp_price = response.xpath('//span[@id="priceblock_ourprice"]/text()').extract_first()
            if temp_price is not None:
                if len(temp_price) > 5:
                    temp_price = temp_price.split(" - ")[0]
            else:
                temp_price = response.xpath('//*[@id="priceblock_snsprice_Based"]/span/text()').extract_first()
                if temp_price is None:
                    temp_price = "can't get"

            # Handle description
            temp_description = response.xpath('//*[@id="productDescription"]//*').extract_first()
            if temp_description is None:
                temp_description = "Nothing"

            # Handle SKU
            temp_sku = response.url.split("/")[-1]

            # Handle image link
            temp_images = response.xpath('//*[@id="landingImage"]/@data-old-hires').extract_first()

            # Handle external URL
            temp_external_url = "https://www.amazon.com/dp/" + response.url.split("/")[-1] + "/?tag=vttgreat-20"


            item = AmazonItem()
            item["Identifier"] = self.count
            item["Type"] = "external"
            item["SKU"] = temp_sku
            item["Name"] = printableString(temp_title)
            item["Published"] = "1"
            item["IsFeatured"] = "0"
            item["VisibilityInCatalogue"] = "visible"
            item["ShortDescription"] = printableString(temp_short_description)
            item["Description"] = printableString(temp_description)
            item["TaxStatus"] = "taxable"
            item["InStock"] = "100"
            item["AllowCustomerReviews"] = "1"
            item["Price"] = temp_price
            item["Categories"] = "Fashion"
            item["Tags"] = ""
            item["Images"] = temp_images
            item["ExternalURL"] = temp_external_url
            item["Position"] = "0"

            self.count += 1
            notif("Success " + response.url.split("/")[-1])
            yield item
        else:
            item = AmazonItem()
            item["Identifier"] = self.count_fail
            item["Name"] = "CAPTCHA"
            item["ExternalURL"] = "https://www.amazon.com/dp/" + response.url.split("/")[-1] + "?tag=vttgreat-20"
            self.count_fail += 1
            yield item