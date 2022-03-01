from scrapy import cmdline
#新建main.py作为项目入口
cmdline.execute("scrapy crawl myjira_spider".split())