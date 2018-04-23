# -*- coding: utf-8 -*-
import scrapy
import time
import uuid

from HouseCrawler.items import SpiderDataSourceItem
from HouseCrawler.mysqldb.spider_data_source_table import SpiderDataSourceTable
from HouseCrawler.utils.cookies_util import CookiesUtil

class AnjukeSimpleCountyUrlSpider(scrapy.Spider):
    name = "AnjukeSimpleCountyUrlSpider"
    default_delay = 3

    def __init__(self, url, *args, **kwargs):
        super(AnjukeSimpleCountyUrlSpider, self).__init__(*args, **kwargs)
        self.cookies = CookiesUtil.get_anjuke_cookies()
        self.start_urls = [url]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_navigation, cookies=self.cookies)

    # 解析导航栏中的新房和二手房的url
    def parse_navigation(self, response):
        navigation_nodes = response.xpath("//a[@_soj='navigation']")
        if navigation_nodes:
            new_house_url = ''
            used_house_url = ''
            for node in navigation_nodes:
                text = node.xpath("./text()").extract_first()
                if text:
                    text = text.strip()
                    if text == u'新 房':
                        new_house_url = node.xpath("./@href").extract_first()
                        continue
                    if text == u'二手房':
                        used_house_url = node.xpath("./@href").extract_first()
            if new_house_url:
                time.sleep(self.default_delay)  # 限速
                yield scrapy.Request(url=new_house_url, callback=self.parse_new_house_urls, cookies=self.cookies)
            if used_house_url:
                time.sleep(self.default_delay)  # 限速
                yield scrapy.Request(url=used_house_url, callback=self.parse_used_house_urls, cookies=self.cookies)

    # 解析新房页面中各个区/县的url
    def parse_new_house_urls(self, response):
        city = response.xpath("//span[@class='city']/text()").extract_first()
        if city:
            city = city.strip()
        county_nodes = response.xpath("//div[@class='item-list area-bd']/div[@class='filter']/a")
        if county_nodes:
            for node in county_nodes:
                county = node.xpath("./text()").extract_first()
                if county:
                    county = county.strip()
                url = node.xpath("./@href").extract_first()
                if url:
                    data = SpiderDataSourceItem()
                    data['id'] = str(uuid.uuid1())
                    data['source_name'] = u"安居客"
                    data['type'] = "new"
                    data['city'] = city
                    data['county'] = county
                    data['url'] = url
                    print data
                    SpiderDataSourceTable.save_data(data=data)

    # 解析二手房页面中各个区/县的url
    def parse_used_house_urls(self, response):
        city = response.xpath("//span[@class='city']/text()").extract_first()
        if city:
            city = city.strip()
        items = response.xpath("//div[@class='div-border items-list']/div[@class='items']")
        if items:
            for item in items:
                label = item.xpath("./span[@class='item-title']/text()").extract_first()
                if u'区域：' == label:
                    county_nodes = item.xpath("./span[@class='elems-l']/a")
                    if county_nodes:
                        for node in county_nodes:
                            county = node.xpath("./text()").extract_first()
                            if county:
                                county = county.strip()
                            url = node.xpath("./@href").extract_first()
                            if url:
                                data = SpiderDataSourceItem()
                                data['id'] = str(uuid.uuid1())
                                data['source_name'] = u"安居客"
                                data['type'] = "used"
                                data['city'] = city
                                data['county'] = county
                                data['url'] = url
                                print data
                                SpiderDataSourceTable.save_data(data=data)
                break