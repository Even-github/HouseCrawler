# -*- coding: utf-8 -*-
import scrapy
import time
import uuid

from HouseCrawler.items import SpiderDataSourceItem
from HouseCrawler.mysqldb.spider_data_source_table import SpiderDataSourceTable
from HouseCrawler.utils.cookies_util import CookiesUtil

class AnjukeCountyUrlSpider(scrapy.Spider):
    name = "AnjukeCountyUrlSpider"
    start_urls = ['https://www.anjuke.com/sy-city.html']
    default_delay = 3

    def __init__(self, *args, **kwargs):
        super(AnjukeCountyUrlSpider, self).__init__(*args, **kwargs)
        self.cookies = CookiesUtil.get_anjuke_cookies()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_city, cookies=self.cookies)

    # 解析城市url
    def parse_city(self, response):
        city_urls = response.xpath("//div[@class='city_list']/a/@href").extract()
        if city_urls:
            for url in city_urls:
                time.sleep(self.default_delay)  # 限速
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
                    if text == u'二手房':
                        used_house_url = node.xpath("./@href").extract_first()
                        break
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
        county_nodes = response.xpath("//div[@class='filter']/a")
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
        county_nodes = response.xpath("//div[@class='div-border items-list']/div[1]/span[@class='elems-l']/a")
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
