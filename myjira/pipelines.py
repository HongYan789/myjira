# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pandas as pd
import csv


class MyjiraPipeline:
    def __init__(self):
        self.f = open("jira_hours.csv", "w", newline='', encoding='utf-8')
        self.writer = csv.writer(self.f)
        self.writer.writerow([
            'name', 'role', 'hours', 'all'
        ])

    def process_item(self, item, spider):
        # data = dict(item)
        # print(data)
        # datafram = pd.DataFrame(data)
        # datafram.to_csv('jira_hours.csv', index=False, sep=',')
        data_list = [
            item['name'], item['role'], item['hours'], item['all']]
        self.writer.writerow(data_list)
        return item

    def close_spider(self, spider):  # 关闭
        self.f.close()