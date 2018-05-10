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

class LianjiaNewHouseSpider(scrapy.Spider):
    name = "LianjiaNewHouseSpider"
    default_delay = 3
    pool = ConnectionPoolCreater.get_pool()
    redis_connection = redis.Redis(connection_pool=pool)
    page_count = 1
    max_page_count = 10  # 只爬取每个区域的前3页信息
    total_page_num = 0  # 实际总页数，初始化为0
    current_county_spell = None  # 当前区域的拼音

    def __init__(self, city, county, url, *args, **kwargs):
        super(LianjiaNewHouseSpider, self).__init__(*args, **kwargs)
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
        self.cookies = CookiesUtil.get_lianjia_cookies()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse_new_house_list,
                                 cookies=self.cookies)

    # 解析新房列表中的所有url
    def parse_new_house_list(self, response):
        url_root = StringUtil.get_com_url_root(response.url) # 网站的根目录，如：https://bj.fang.lianjia.com
        relative_urls = response.xpath("//ul[@class='resblock-list-wrapper']/li[@class='resblock-list']/a[@class='resblock-img-wrapper']/@href").extract()
        if relative_urls:
            for relative_url in relative_urls:
                url = url_root + relative_url
                # 已经爬过的url不再爬
                if self.redis_connection.sismember('crawledUrls', url) is False:
                    yield scrapy.Request(url=url,
                                         callback=self.parse_new_house_details,
                                         cookies=self.cookies,
                                         meta={'detail_url': url})
        # 获取总页数
        if self.total_page_num == 0:
            # 数据总数
            total_size = response.xpath("//div[@class='resblock-have-find']/span[@class='value']/text()").extract_first()
            total_size = re.sub(r'\s', '', total_size)
            if total_size:
                self.total_page_num = round(int(total_size) / 10)  # 总页数
        # 只抓取前几页数据
        if self.page_count < self.max_page_count and self.page_count < self.total_page_num:
            if self.current_county_spell is None:
                self.current_county_spell = StringUtil.get_url_current_catalog(response.url)
            self.page_count = self.page_count + 1
            next_page_url = url_root \
                            + '/loupan/' \
                            + self.current_county_spell \
                            + '/pg' + str(self.page_count) \
                            + '/#' + self.current_county_spell
            print 'page:' + str(self.page_count - 1) + '/' + str(self.max_page_count)
            yield scrapy.Request(url=next_page_url,
                                 callback=self.parse_new_house_list,
                                 cookies=self.cookies)

    # 解析楼盘详情页中的详细信息
    def parse_new_house_details(self, response):
        item = HousecrawlerItem()
        item['id'] = str(uuid.uuid1())
        item['province'] = None
        item['city'] = self.address['city']
        item['county'] = self.address['county']
        item['url'] = response.url
        item['crawl_time'] = time.time()
        item['source'] = u'链家网'
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

        unit = response.xpath("//span[@class='yuan']/text()").extract_first()
        if unit:
            if StringUtil.container_tao(unit) is False:
                unit_price = response.xpath("//span[@class='junjia']/text()").extract_first()
                if unit_price:
                    item['unit_price'] = StringUtil.get_first_int_from_string(unit_price)

                house_name = response.xpath("//h1[@class='DATA-PROJECT-NAME']/text()").extract_first()
                if house_name:
                    item['house_name'] = re.sub(r'\s', '', house_name)

                detail_box = response.xpath("//div[@class='box-loupan']/p[@class='desc-p clear']")
                if detail_box:
                    for li in detail_box:
                        label = li.xpath("./span[@class='label']/text()").extract_first()
                        label = re.sub(r'\s', '', label)
                        if u'项目地址：' == label:
                            house_address = li.xpath("./span[@class='label-val']/text()").extract_first()
                            if house_address:
                                item['house_address'] = re.sub(r'\s', '', house_address)
                            break

                li_list = response.xpath("//ul[@class='table-list clear']/li/p[@class='desc-p clear']")
                if li_list:
                    for li in li_list:
                        label = li.xpath("./span[@class='label']/text()").extract_first()
                        label = re.sub(r'\s', '', label)
                        if u'交房时间：' == label:
                            house_data = li.xpath("./span[@class='label-val']/text()").extract_first()
                            item['build_year'] = StringUtil.get_first_year_from_string(house_data)
                            break

        self.redis_connection.sadd('crawledUrls', response.meta['detail_url'])
        print item # 测试用
        self.check_and_save(item)
        return item

    def check_and_save(self, item):
        if item:
            if item['unit_price']:
                HouseTable.save_data(data=item)


