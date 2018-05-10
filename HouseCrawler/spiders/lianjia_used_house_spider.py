# -*- coding: utf-8 -*-
import scrapy
import time
import re
import uuid
import redis

from HouseCrawler.utils.cookies_util import CookiesUtil
from HouseCrawler.items import HousecrawlerItem
from HouseCrawler.mysqldb.house_table import HouseTable
from HouseCrawler.items import AddressItem
from HouseCrawler.utils.string_util import StringUtil
from HouseCrawler.mysqldb.province_city_table import ProvinceCity
from HouseCrawler.redis.connection_pool_creater import ConnectionPoolCreater

class LianjiaUsedHouseSpider(scrapy.Spider):
    name = "LianjiaUsedHouseSpider"
    default_delay = 3
    pool = ConnectionPoolCreater.get_pool()
    redis_connection = redis.Redis(connection_pool=pool)
    page_count = 1
    max_page_count = 4  # 只爬取每个区域的前3页信息
    total_page_num = 0  # 实际总页数，初始化为0

    def __init__(self, city, county, url, *args, **kwargs):
        super(LianjiaUsedHouseSpider, self).__init__(*args, **kwargs)
        if url:
            self.url = url
            self.start_urls = [self.url]
            self.address = AddressItem()
            # 控制台执行时，用下列四行代码
            if city:
                self.address['city'] = city.decode('gbk') # 控制台的编码方式是gbk，此处需要按gbk解码
            if county:
                self.address['county'] = county.decode('gbk')
            # HTTP调用时，用下列两行代码
            # self.address['city'] = city
            # self.address['county'] = county
        self.cookies = CookiesUtil.get_lianjia_cookies()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse_used_house_list,
                                 cookies=self.cookies)

    # 解析二手房列表中的所有url
    def parse_used_house_list(self, response):
        detail_urls = response.xpath("//ul[@class='sellListContent']//li[@class='clear']/a/@href").extract()
        if detail_urls:
            for detail_url in detail_urls:
                # 已经爬过的url不再爬
                if self.redis_connection.sismember('crawledUrls', detail_url) is False:
                    yield scrapy.Request(url=detail_url,
                                         callback=self.parse_used_house_details,
                                         cookies=self.cookies,
                                         meta={'detail_url': detail_url})
        # 获取总页数
        if self.total_page_num == 0:
            # 数据总数
            total_size = response.xpath("//h2[@class='total fl']/span/text()").extract_first()
            total_size = re.sub(r'\s', '', total_size)
            if total_size:
                self.total_page_num = round(int(total_size) / 30)  # 总页数
        # 只抓取前几页数据
        if self.page_count < self.max_page_count and self.page_count < self.total_page_num:
            self.page_count = self.page_count + 1
            next_page_url = self.url + 'pg' + str(self.page_count) + '/'
            print 'page:' + str(self.page_count - 1) + '/' + str(self.max_page_count)
            yield scrapy.Request(url=next_page_url,
                                 callback=self.parse_used_house_list,
                                 cookies=self.cookies)

    # 解析二手房详情页中的详细信息
    def parse_used_house_details(self, response):
        item = HousecrawlerItem()
        item['id'] = str(uuid.uuid1())
        item['province'] = None
        item['city'] = self.address['city']
        item['county'] = self.address['county']
        item['url'] = response.url
        item['crawl_time'] = time.time()
        item['source'] = u'链家网'
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

        house_name = response.xpath("//div[@class='title-wrapper']/div[@class='content']/div[@class='title']/h1[@class='main']/@title").extract_first()
        if house_name:
            item['house_name'] = re.sub(r'\s', '', house_name)
        content_container = response.xpath("//div[@class='content']")
        if content_container:
            price_container = content_container.xpath("./div[@class='price ']")
            if price_container:
                total_price = price_container.xpath("./span[@class='total']/text()").extract_first()
                if total_price:
                    item['total_price'] = re.sub(r'\s', '', total_price)
                unit_price = price_container.xpath("./div[@class='text']/div[@class='unitPrice']/span[@class='unitPriceValue']/text()").extract_first()
                if unit_price:
                    item['unit_price'] = StringUtil.get_first_int_from_string(unit_price)
            build_year_str = content_container.xpath("./div[@class='houseInfo']/div[@class='area']/div[@class='subInfo']/text()").extract_first()
            if build_year_str:
                item['build_year'] = StringUtil.get_first_year_from_string(build_year_str)
            house_address = content_container.xpath("./div[@class='aroundInfo']/div[@class='areaName']/a[@class='supplement']/text()").extract_first()
            if house_address:
                item['house_address'] = re.sub(r'\s', '', house_address)

        self.redis_connection.sadd('crawledUrls', response.meta['detail_url'])
        print item # 测试用
        self.check_and_save(item)
        return item

    def check_and_save(self, item):
        if item:
            if item['unit_price']:
                HouseTable.save_data(data=item)


