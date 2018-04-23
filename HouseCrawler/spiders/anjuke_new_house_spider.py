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

class AnjukeNewHouseSpider(scrapy.Spider):
    name = "AnjukeNewHouseSpider"
    default_delay = 3
    pool = ConnectionPoolCreater.get_pool()
    redis_connection = redis.Redis(connection_pool=pool)

    def __init__(self, city, county, url, *args, **kwargs):
        super(AnjukeNewHouseSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
            self.address = AddressItem()
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
            yield scrapy.Request(url=url, 
                                 callback=self.parse_new_house_list, 
                                 cookies=self.cookies)

    # 解析新房列表中的所有url
    def parse_new_house_list(self, response):
        urls = response.xpath("//div[@class='key-list']/div[@class='item-mod']/@data-link | //div[@class='key-list']/div[@class='item-mod ']/@data-link")\
            .extract()
        if urls:
            for url in urls:
                # 已经爬过的url不再爬
                if self.redis_connection.sismember('crawledUrls', url) is False:
                    yield scrapy.Request(url=url,
                                         callback=self.parse_new_house_homepage,
                                         meta={'homepage_url': url})
        # 下一页
        next_page = response.xpath("//a[@class='next-page next-link']/@href").extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_new_house_list,
                                 cookies=self.cookies)

    # 解析楼盘首页导航栏中“楼盘详情”url
    def parse_new_house_homepage(self, response):
        detail_url = response.xpath("//ul[@class='lp-navtabs clearfix']/li[2]/a/@href").extract_first()
        if detail_url:
            yield scrapy.Request(url=detail_url,
                                 callback=self.parse_new_house_details,
                                 cookies=self.cookies,
                                 meta=response.meta)

    # 解析楼盘详情页中的详细信息
    def parse_new_house_details(self, response):
        item = HousecrawlerItem()
        item['id'] = str(uuid.uuid1())
        item['province'] = None
        item['city'] = self.address['city']
        item['county'] = self.address['county']
        item['url'] = response.url
        item['crawl_time'] = time.time()
        item['source'] = u'安居客'
        item['type'] = u'new'
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
        basic_info_list = response.xpath("//div[@class='can-left']/div[1]/div[@class='can-border']/ul[@class='list']/li")
        sale_info_list = response.xpath("//div[@class='can-left']/div[2]/div[@class='can-border']/ul[@class='list']/li")
        # 基本信息
        if basic_info_list:
            for li in basic_info_list:
                label = li.xpath("./div[@class='name']/text()").extract_first()
                if u'楼盘名称' == label:
                    house_name = li.xpath("./div[@class='des']/a/text()").extract_first()
                    if house_name:
                        item['house_name'] = re.sub(r'\s', '', house_name)
                    continue
                if u'参考单价' == label:
                    unit_price = li.xpath("./div[@class='des']/span/text()").extract_first()
                    if unit_price:
                        item['unit_price'] = StringUtil.get_first_int_from_string(unit_price)
                    continue
                if u'楼盘总价' == label:
                    total_price = li.xpath("./div[@class='des']/span/text()").extract_first()
                    if total_price:
                        item['total_price'] = StringUtil.get_first_int_from_string(total_price)
                    continue
                if u'楼盘地址' == label:
                    house_address = li.xpath("./div[@class='des']/text()").extract_first()
                    if house_address:
                        item['house_address'] = re.sub(r'\s', '', house_address)
                    continue
        # 销售信息
        if sale_info_list:
            for li in sale_info_list:
                label = li.xpath("./div[@class='name']/text()").extract_first()
                if u'最低首付' == label:
                    down_payment_str = li.xpath("./div[@class='des']/text()").extract_first()
                    if down_payment_str:
                        item['down_payment'] = StringUtil.get_first_number_from_string(down_payment_str)
                    continue
                if u'月供' == label:
                    monthly_payment_str = li.xpath("./div[@class='des']/text()").extract_first()
                    if monthly_payment_str:
                        item['monthly_payment'] = StringUtil.get_first_number_from_string(monthly_payment_str)
                    continue
                if u'交房时间' == label:
                    build_year_str = li.xpath("./div[@class='des']/text()").extract_first()
                    if build_year_str:
                        item['build_year'] = StringUtil.get_first_year_from_string(build_year_str)
                    continue
        self.redis_connection.sadd('crawledUrls', response.meta['homepage_url'])
        # print item # 测试用
        self.check_and_save(item)
        return item

    def check_and_save(self, item):
        if item:
            if item['unit_price']:
                HouseTable.save_data(data=item)


