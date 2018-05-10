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
    page_count = 1
    max_page_count = 2 # 只爬取每个区域的前2页信息

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
        # 只抓取前几页数据
        if self.page_count < self.max_page_count:
            next_page = response.xpath("//a[@class='aNxt']/@href").extract_first()
            if next_page:
                self.page_count = self.page_count + 1
                print 'page:' + str(self.page_count) + '/' + str(self.max_page_count)
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
            first_col = details_info.xpath("./div[@class='first-col detail-col']/dl")
            third_col = details_info.xpath("./div[@class='third-col detail-col']/dl")
            if first_col:
                for dl in first_col:
                    first_label = dl.xpath('./dt/text()').extract_first()
                    if u'所属小区：' == first_label:
                        house_name = dl.xpath("./dd/a/text()").extract_first()
                        if house_name:
                            item['house_name'] = re.sub(r'\s', '', house_name)
                        continue
                    if u'所在位置：' == first_label:
                        house_address_str = dl.xpath("./dd/p/text()").extract()
                        if house_address_str:
                            house_address = re.sub('\s|－', '', house_address_str[-1])
                            item['house_address'] = house_address[1:]
                        continue
                    if u'建造年代：' == first_label:
                         build_year_str = dl.xpath("./dd/text()").extract_first()
                         if build_year_str:
                            item['build_year'] = StringUtil.get_first_int_from_string(build_year_str)
            if third_col:
                for dl in third_col:
                    label = dl.xpath('./dt/text()').extract_first()
                    if u'房屋单价：' == label:
                        unit_price_str = dl.xpath("./dd/text()").extract_first()
                        if unit_price_str:
                            item['unit_price'] = StringUtil.get_first_int_from_string(unit_price_str)
                        continue
                    if u'参考首付：' == label:
                        down_payment_str = dl.xpath("./dd/text()").extract_first()
                        if down_payment_str:
                            item['down_payment'] = StringUtil.get_first_number_from_string(down_payment_str)
                        continue
                    if u'参考月供：' == label:
                        monthly_payment_str = dl.xpath("./dd/span/text()").extract_first()
                        if monthly_payment_str:
                            item['monthly_payment'] = StringUtil.get_first_number_from_string(monthly_payment_str)
                        continue

        total_price = response.xpath("//div[@class='basic-info clearfix']/span[@class='light info-tag']/em/text()").extract_first()
        if total_price:
            item['total_price'] = re.sub(r'\s', '', total_price)
        print item  # 测试用
        self.redis_connection.sadd('crawledUrls', response.url)
        self.check_and_save(item=item)
        return item

    def check_and_save(self, item):
        if item:
            if item['unit_price']:
                HouseTable.save_data(data=item)