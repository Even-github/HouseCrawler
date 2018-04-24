# -*- coding: utf-8 -*-
import scrapy
import time
import re
import uuid
import redis

from HouseCrawler.utils.cookies_util import CookiesUtil
from HouseCrawler.items import HousecrawlerItem
from HouseCrawler.items import AddressItem
from HouseCrawler.mysqldb.house_table import HouseTable
from HouseCrawler.utils.string_util import StringUtil
from HouseCrawler.mysqldb.province_city_table import ProvinceCity
from HouseCrawler.redis.connection_pool_creater import ConnectionPoolCreater

class AnjukeUsedHouseSpider(scrapy.Spider):
    name = "AnjukeUsedHouseSpider"
    default_delay = 1000
    pool = ConnectionPoolCreater.get_pool()
    redis_connection = redis.Redis(connection_pool=pool)
    max_required_count = 150 # 由于爬取的数量较多，每一个区域限定爬取数量
    required_count = 0 # 记录爬取了多少个信息

    def __init__(self, city, county, url, *args, **kwargs):
        super(AnjukeUsedHouseSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
            self.address = AddressItem()
            # 计算爬取页面的数量，当数量大于一定数量时，暂停爬虫一段时间
            self.count = 0
            # 控制台执行时，用下列四行代码
            # if city:
            #     self.address['city'] = city.decode('gbk') # 控制台的编码方式是gbk，此处需要按gbk解码
            # if county:
            #     self.address['county'] = county.decode('gbk')
            # HTTP调用时，用下列两行代码
            self.address['city'] = city
            self.address['county'] = county
        self.cookies = CookiesUtil.get_anjuke_cookies()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_used_house_list, cookies=self.cookies)

    # 解析二手房列表中的所有url
    def parse_used_house_list(self, response):
        if self.required_count < self.max_required_count:
            urls = response.xpath("//ul[@id='houselist-mod-new']/li[@class='list-item']/div[@class='house-details']/div[@class='house-title']/a/@href").extract()
            if urls:
                for url in urls:
                    # 已经爬过的url不再爬
                    if self.redis_connection.sismember('crawledUrls', url) is False:
                        self.count = self.count + 1
                        # 爬取一定数量的页面后，暂停一段时间
                        if self.count > 430:
                            print 'Spider is preparing to sleep...'
                            time.sleep(self.default_delay)
                            self.count = 0
                        yield scrapy.Request(url=url,
                                             callback=self.parse_used_house_details,
                                             cookies=self.cookies)
            next_page = response.xpath("//a[@class='aNxt']/@href").extract_first()
            if next_page:
                yield scrapy.Request(url=next_page,
                                     callback=self.parse_used_house_list,
                                     cookies=self.cookies)

    # 解析二手房的详细信息
    def parse_used_house_details(self, response):
        item = HousecrawlerItem()
        item['id'] = str(uuid.uuid1())
        item['province'] = None
        item['city'] = self.address['city']
        item['county'] = self.address['county']
        item['url'] = response.url
        item['crawl_time'] = time.time()
        item['source'] = u'安居客'
        item['type'] = u'used'
        item['house_name'] = None
        item['unit_price'] = None
        item['total_price'] = None
        item['house_address'] = None
        item['down_payment'] = None
        item['monthly_payment'] = None
        item['build_year'] = None
        item['description'] = None
        if item['city']:
            item['province'] = ProvinceCity.select_province_by_city(item['city'])
        details_info = response.xpath("//div[@class='block-wrap block-nocopy no-bd-top']/div/div")
        if details_info:
            first_col = details_info.xpath("./div[@class='first-col detail-col']")
            third_col = details_info.xpath("./div[@class='third-col detail-col']")
            if first_col:
                house_name = first_col.xpath("./dl[1]/dd/a/text()").extract_first()
                if house_name:
                    item['house_name'] = re.sub(r'\s', '', house_name)
                house_address_str = first_col.xpath("./dl[2]/dd/p/text()").extract()
                if house_address_str:
                    house_address = re.sub('\s|－', '', house_address_str[-1])
                    item['house_address'] = house_address[1:]
                build_year_str = first_col.xpath("./dl[3]/dd/text()").extract_first()
                if build_year_str:
                    item['build_year'] = StringUtil.get_first_int_from_string(build_year_str)
            if third_col:
                unit_price_str = third_col.xpath("./dl[2]/dd/text()").extract_first()
                if unit_price_str:
                    item['unit_price'] = StringUtil.get_first_int_from_string(unit_price_str)
                down_payment_str = third_col.xpath("./dl[3]/dd/text()").extract_first()
                if down_payment_str:
                    item['down_payment'] = StringUtil.get_first_number_from_string(down_payment_str)
                monthly_payment_str = third_col.xpath("./dl[4]/dd/span/text()").extract_first()
                if monthly_payment_str:
                    item['monthly_payment'] = StringUtil.get_first_number_from_string(monthly_payment_str)
        total_price = response.xpath("//div[@class='basic-info clearfix']/span[@class='light info-tag']/em/text()").extract_first()
        if total_price:
            item['total_price'] = re.sub(r'\s', '', total_price)
        print item  # 测试用
        self.redis_connection.sadd('crawledUrls', response.url)
        self.check_and_save(item=item)
        self.required_count = self.required_count + 1
        print 'required_count:' + str(self.required_count)
        return item

    def check_and_save(self, item):
        if item:
            if item['unit_price']:
                HouseTable.save_data(data=item)