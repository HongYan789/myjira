##如何采用scrapy框架进行项目爬虫操作

###步骤一：创建scrapy项目
```shell
scrapy startproject myjira
```


###步骤二:生成爬虫核心类
```shell
cd spiders
scrapy genspider myjira_spider 'jira.lp.com'
```



###步骤三:编写爬虫items.py
```python
import scrapy


class MyjiraItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    role = scrapy.Field()
    hours = scrapy.Field()
    all = scrapy.Field()

```


###步骤四:编写核心爬虫类myjira_spider.py
```python
from myjira.items import MyjiraItem
#在指定目录下采用 scrapy genspider xxx_spider xxx.com 命令生成爬虫xpath及正则表达式处理py类（即爬虫处理类）
class MyjiraSpiderSpider(scrapy.Spider):
    #爬虫项目名
    name = 'myjira_spider'
    #爬虫网站（允许的域名）
    allowed_domains = ['jira.lp.com']
    #爬虫完整路径（入口url，扔到调度器）
    start_urls = ['http://jira.lp.com/secure/resourceManagerAction%21mainpage.jspa?tabId=1&queryType=1&dept_field_id=-1&group_field_id=-1&domain_field_id=-1&begintime=2022-02-14&endtime=2022-02-20']

    # def start_requests(self):  # 请求时携带Cookies
    #     cookies = '_ga=GA1.2.148246823.1630290497; atlassian.xsrf.token=BZ6T-RW2W-L1ZP-A4HR|8c660558adfaec963c3f435af7eacaafa8a88593|lout; Hm_lvt_f8e42400dd4c16e4b8dc8e193c6adc34=1645606030,1646018701; Hm_lpvt_f8e42400dd4c16e4b8dc8e193c6adc34=1646019876; JSESSIONID=B7AA754F70315E04EFB0F652F13F6378'
    #     cookies = {i.split('=')[0]: i.split('=')[1] for i in cookies.split('; ')}
    #     yield scrapy.Request(self.start_urls[0], cookies=cookies)

    #默认的解析方法
    def parse(self, response):
       # print(response.text)
       #绝对路径
       jira_list = response.xpath("//*[@id='mainForm']/div[1]/div[2]/table/tbody/tr")
       for jira in jira_list:
           # 解析为<Selector>数据
           # 引入咱们的items(导入items文件)，进行数据解析
           jira_item = MyjiraItem()
           # 直接解析其中为./text()的数据，且取第一条(相对路径)
           #进行详细的数据解析
           jira_item['name'] = jira.xpath("./td[1]/text()").extract_first()
           jira_item['role'] = jira.xpath("./td[2]/text()").extract_first()
           jira_item['hours'] = jira.xpath("./td[3]/a/text()").extract_first()
           jira_item['all'] = jira.xpath("./td/a/text()").extract()
           # print(jira_item)
       #需要将我们的数据yield到管道中，否则管道中是无法接收到数据的(需要将我们的数据，yield到pipeline里面去)
           yield jira_item

       #如果存在分页情况，则需要用到回调函数来解决
       # 例如:解析下一页规则，取后一页的xpath
       next_link = response.xpath("//sapn[@class='next']/link/@href").extract()
       if next_link:
           next_link = next_link[0]
           yield scrapy.Request('http://xxx/xxx'+next_link,callback=self.parse())


```


###步骤五:编写管道pipelines.py文件
```python
import csv

class MyjiraPipeline:
    def __init__(self):
        self.f = open("jira_hours.csv", "w", newline='', encoding='utf-8')
        self.writer = csv.writer(self.f)
        self.writer.writerow([
            'name', 'role', 'hours', 'all'
        ])

    def process_item(self, item, spider):
        data_list = [
            item['name'], item['role'], item['hours'], item['all']]
        self.writer.writerow(data_list)
        return item

    def close_spider(self, spider):  # 关闭
        self.f.close()

```

###步骤六:在middlewares.py文件中编写useragent伪装类
```python
import random

#useragent伪装类
class my_useragent(object):
    def process_request(self,request,spider):
        USER_AGENT_LIST = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
            "Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50",
            "Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50",
            "Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0;",
            "Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)",
            "Mozilla/4.0(compatible;MSIE6.0;WindowsNT5.1)",
            "Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1",
            "Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1",
            "Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11",
            "Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11",
            "Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)",
            "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)"
        ]
        USER_AGENT = random.choice(USER_AGENT_LIST)
        request.headers['USER_Agent'] = USER_AGENT
```

###步骤七:打开settings.py 文件更改配置
```python
#一定要开启pipeline选项，否则数据是无法保存到我们的数据库中
ITEM_PIPELINES = {
   'myjira.pipelines.MyjiraPipeline': 300,
}

#开启useragent伪装类
DOWNLOADER_MIDDLEWARES = {
   'myjira.middlewares.my_useragent': 543,
}

```


###步骤八:编写入口类main.py
```python
from scrapy import cmdline
#新建main.py作为项目入口
cmdline.execute("scrapy crawl myjira_spider".split())

```

###步骤九:运行入口类main.py，观察数据结果：jira_hours.csv

