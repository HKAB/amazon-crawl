# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from scrapy import signals
from scrapy.exporters import CsvItemExporter

class AmazonPipeline(object):
	def __init__(self):
		self.files = {}
	def open_spider(self, spider):
		file_csv = open('%s_items.csv' % spider.name, 'w+b')
		self.files[spider] = file_csv
		self.exporter = CsvItemExporter(file_csv, fields_to_export=["Identifier", "Type", "SKU", "Name", "Published", "IsFeatured", "VisibilityInCatalogue", "ShortDescription", "Description", "TaxStatus", "InStock", "AllowCustomerReviews", "Price", "Categories", "Tags", "Images", "ExternalURL", "Position"])
		self.exporter.start_exporting()
	def close_spider(self, spider):
		self.exporter.finish_exporting()
		file = self.files.pop(spider)
		file.close()
	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item