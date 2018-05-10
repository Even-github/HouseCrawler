# -*- coding: utf-8 -*-
import scrapy
import time
import uuid

from HouseCrawler.items import SpiderDataSourceItem
from HouseCrawler.mysqldb.spider_data_source_table import SpiderDataSourceTable
from HouseCrawler.utils.cookies_util import CookiesUtil

class LianjiaCountyUrlSpider(scrapy.Spider):
    name = "LianjiaCountyUrlSpider"
    start_urls = ['https://bj.lianjia.com/']
    default_delay = 3

    def __init__(self, *args, **kwargs):
        super(LianjiaCountyUrlSpider, self).__init__(*args, **kwargs)
        self.cookies = CookiesUtil.get_anjuke_cookies()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_new_hosue_url, cookies=self.cookies)

    def parse_new_hosue_url(self, response):
        navigation_item_list = response.xpath("//div[@class='nav typeUserInfo']/ul/li")
        if navigation_item_list:
            for li in navigation_item_list:
                title = li.xpath("./a/text()").extract_first()
                if title == u'新房':
                    new_house_url = li.xpath("./a/@href").extract_first()
                    time.sleep(self.default_delay)  # 限速
                    yield scrapy.Request(url=new_house_url, callback=self.parse_city_url, cookies=self.cookies)
                    break

    # 解析各城市的url
    def parse_city_url(self, response):
        city_url_list = response.xpath("//div[@class='city-enum fl']/a")
        if city_url_list:
            for city_item in city_url_list:
                city_name = city_item.xpath("./text()").extract_first()
                city_url = 'https:' + city_item.xpath("./@href").extract_first()
                time.sleep(self.default_delay)  # 限速
                yield scrapy.Request(url=city_url,
                                     callback=self.parse_entrance_url,
                                     cookies=self.cookies,
                                     meta={'city': city_name})

    # 解析新房和二手房列表的入口url
    def parse_entrance_url(self, response):
        navigation_list = response.xpath("//ul[@class='nav-list']/li/a")
        if navigation_list:
            for item in navigation_list:
                title = item.xpath("./text()").extract_first()
                if title == u'楼盘':
                    new_url = response.url + item.xpath("./@href").extract_first()
                    time.sleep(self.default_delay)  # 限速
                    yield scrapy.Request(url=new_url,
                                         callback=self.parse_new_county_url,
                                         cookies=self.cookies,
                                         meta=response.meta)
                    break
        header_list = response.xpath("//header[@class='new-header']/div[@class='float-wrapper']/ul[@class='link-list-wrapper']/li/a")
        if header_list:
            for item in header_list:
                label = item.xpath("./text()").extract_first()
                if label == u'二手房':
                    used_url = 'https:' + item.xpath("./@href").extract_first()
                    time.sleep(self.default_delay)  # 限速
                    yield scrapy.Request(url=used_url,
                                         callback=self.parse_used_entrance_url,
                                         cookies=self.cookies,
                                         meta=response.meta)
                    break

    # 解析新房楼盘页面中的地区url
    def parse_new_county_url(self, response):
        li_list = response.xpath("//ul[@class='district-wrapper']/li")
        if li_list:
            for li in li_list:
                county_name = li.xpath("./text()").extract_first()
                spell = li.xpath("./@data-district-spell").extract_first()
                url = response.url + spell + '/#' + spell

                data = SpiderDataSourceItem()
                data['id'] = str(uuid.uuid1())
                data['source_name'] = u"链家网"
                data['type'] = "new"
                data['city'] = response.meta['city']
                data['county'] = county_name
                data['url'] = url
                print data
                SpiderDataSourceTable.save_data(data=data)
                return data

    # 解析二手房列表入口url
    def parse_used_entrance_url(self, response):
        navigation_item_list = response.xpath("//div[@class='nav typeUserInfo']/ul/li")
        if navigation_item_list:
            for li in navigation_item_list:
                title = li.xpath("./a/text()").extract_first()
                if title == u'二手房':
                    used_house_url = li.xpath("./a/@href").extract_first()
                    my_meta = response.meta
                    my_meta['basic_url'] = response.url
                    time.sleep(self.default_delay)  # 限速
                    yield scrapy.Request(url=used_house_url,
                                         callback=self.parse_used_county_url,
                                         cookies=self.cookies,
                                         meta=my_meta)
                    break

    # 解析二手房页面中的地区url
    def parse_used_county_url(self, response):
        county_list = response.xpath("//div[@data-role='ershoufang']/div/a")
        if county_list:
            for li in county_list:
                county_name = li.xpath("./text()").extract_first()
                part_url = li.xpath("./@href").extract_first()
                url = response.meta['basic_url'] + part_url

                data = SpiderDataSourceItem()
                data['id'] = str(uuid.uuid1())
                data['source_name'] = u"链家网"
                data['type'] = "used"
                data['city'] = response.meta['city']
                data['county'] = county_name
                data['url'] = url
                print data
                SpiderDataSourceTable.save_data(data=data)
                return data