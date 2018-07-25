# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

class WuhanFangPipeline(object):

    def process_item(self, item, spider):
        print(json.dumps(item, sort_keys=True, ensure_ascii=False, indent=4))
        return item
