# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.settings import Settings
from scrapy.exporters import CsvItemExporter
from utils import isASCIIString, notif

class AmazonPipeline(object):
	def __init__(self):
		self.files = {}
		self.item_fail = [["External URL", "Status"]]
	def open_spider(self, spider):
		file_csv = open('%s_items.csv' % spider.name, 'w+b')
		self.files[spider] = file_csv
		self.exporter = CsvItemExporter(file_csv, fields_to_export=["Identifier", "Type", "SKU", "Name", "Published", "IsFeatured", "VisibilityInCatalogue", "ShortDescription", "Description", "TaxStatus", "InStock", "AllowCustomerReviews", "Price", "Categories", "Tags", "Images", "ExternalURL", "Position"])
		self.exporter.start_exporting()
	def close_spider(self, spider):
		self.exporter.finish_exporting()
		file = self.files.pop(spider)
		file.close()
		import csv
		fields = ["Identifier", "Type", "SKU", "Name", "Published", "Is Featured", "Visibility In Catalogue", "Short Description", "Description", "Tax tatus", "In Stock", "Allow Customer Reviews", "Price", "Categories", "Tags", "Images", "External URL", "Position"]
		with open('%s_items.csv' % spider.name, 'r') as f_read:
			reader = csv.reader(f_read)
			data = list(reader)
			if len(data) > 0:
				data[0] = fields
		# https://stackoverflow.com/questions/3191528/csv-in-python-adding-an-extra-carriage-return-on-windows
		with open('%s_items.csv' % spider.name, 'w+b') as f_write:
			writer = csv.writer(f_write)
			writer.writerows(data)

		fields_fail = ["Identifier", "Name", "External URL"]
		with open('%s_items_fail.csv' % spider.name, 'r') as f_read_fail:
			reader = csv.reader(f_read_fail)
			data = list(reader)
			if len(data) > 0:
				data[0] = fields_fail
		# https://stackoverflow.com/questions/3191528/csv-in-python-adding-an-extra-carriage-return-on-windows
		with open('%s_items_fail.csv' % spider.name, 'w+b') as f_write_fail:
			writer = csv.writer(f_write_fail)
			writer.writerows(self.item_fail)

		f_read_fail.close()
		f_read.close()
		f_write.close()
		f_write_fail.close()
	def process_item(self, item, spider):
		max_product = spider.settings.get("CLOSESPIDER_ITEMCOUNT")
		# notif("max_product: " + str(max_product))
		if max_product != 0:
			if int(item["Identifier"]) < int(max_product):
				if (not isASCIIString(item["Name"])) or (item["Name"] == "CAPTCHA") or (item["Name"] == "404 Not Found") or (item["Price"] == "can't get"):
					self.item_fail.append(item.values())
				else:
					self.exporter.export_item(item)
		else:
			if (not isASCIIString(item["Name"])) or (item["Name"] == "CAPTCHA") or (item["Name"] == "404 Not Found") or (item["Price"] == "can't get"):
					self.item_fail.append(item.values())
			else:
				self.exporter.export_item(item)
		return item