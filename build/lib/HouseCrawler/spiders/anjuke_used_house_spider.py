# -*- coding: utf-8 -*-
import scrapy
import time
import re
import uuid

from HouseCrawler.utils.cookies_util import CookiesUtil
from HouseCrawler.items import HousecrawlerItem
from HouseCrawler.items import AddressItem
from HouseCrawler.db.house_table import HouseTable
from HouseCrawler.utils.string_util import StringUtil
from HouseCrawler.db.province_city_table import ProvinceCity

class AnjukeUsedHouseSpider(scrapy.Spider):
    name = "AnjukeUsedHouseSpider"
    default_delay = 3

    def __init__(self, city, county, url, *args, **kwargs):
        super(AnjukeUsedHouseSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
            self.address = AddressItem()
            if city:
                self.address['city'] = city.decode('gbk')
            if county:
                self.address['county'] = county.decode('gbk')
        self.cookies = CookiesUtil.get_anjuke_cookies()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_used_house_list, cookies=self.cookies)

    # 解析二手房列表中的所有url
    def parse_used_house_list(self, response):
        urls = response.xpath("//ul[@id='houselist-mod-new']/li[@class='list-item']/div[@class='house-details']/div[@class='house-title']/a/@href").extract()
        if urls:
            for url in urls:
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
        details_info = response.xpath("//div[@class='houseInfoV2-wrap']/div[@class='houseInfoV2-detail clearfix']")
        if details_info:
            first_col = details_info.xpath("./div[@class='first-col detail-col']")
            third_col = details_info.xpath("./div[@class='third-col detail-col']")
            if first_col:
                house_name = first_col.xpath("./dl[1]/dd/a/text()").extract_first()
                if house_name:
                    item['house_name'] = re.sub(r'\s', '', house_name)
                house_address_str = first_col.xpath("./dl[2]/dd/p/text()").extract()
                if house_address_str:
                    item['house_address'] = ''
                    for s in house_address_str:
                        s = re.sub(r'\s', '', s)
                        item['house_address'] = item['house_address'] + s
                build_year_str = first_col.xpath("./dl[3]/dd/text()").extract_first()
                if build_year_str:
                    item['build_year'] = StringUtil.get_first_int_from_string(build_year_str)
            if third_col:
                unit_price_str = third_col.xpath("./dl[2]/dd/text()").extract_first()
                if unit_price_str:
                    item['unit_price'] = StringUtil.get_first_int_from_string(unit_price_str)
                down_payment_str = third_col.xpath("./dl[3]/dd/text()").extract_first()
                if down_payment_str:
                    item['down_payment'] = StringUtil.get_first_float_from_string(down_payment_str)
                monthly_payment_str = third_col.xpath("./dl[4]/dd/sapn/text()").extract_first()
                if monthly_payment_str:
                    item['monthly_payment'] = StringUtil.get_first_float_from_string(monthly_payment_str)
        total_price = response.xpath("//div[@class='basic-info clearfix']/span[@class='light info-tag']/em/text()").extract_first()
        if total_price:
            item['total_price'] = re.sub(r'\s', '', total_price)
        print item  # 测试用
        HouseTable.save_data(data=item)
        return item