import scrapy


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

