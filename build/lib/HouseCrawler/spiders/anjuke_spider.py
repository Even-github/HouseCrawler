# -*- coding: utf-8 -*-
import scrapy
import re
import time
import random

from HouseCrawler.items import HousecrawlerItem
from HouseCrawler.items import AddressItem

class AnjukeSpider(scrapy.Spider):
    name = "AnjukeSpider"
    start_urls = ['https://www.anjuke.com/sy-city.html']
    cookies = {
        'aQQ_ajkguid': '53AF0A50-2028-B38D-2CF1-C1BF7192E9FB',
        'ctid': '107 ',
        '_ga': 'GA1.2.225350737.1513871159',
        '58tj_uuid': 'd169abf8-5750-4213-920a-45eb37c93d6c',
        'new_uv': '22',
        'als': '0',
        'isp': 'true',
        'Hm_lvt_c5899c8768ebee272710c9c5f365a6d8': '1514165902,1514254898,1514277658,1514290019',
        'propertys': 'hsc6vq-p1kjyo_hma9vh-p1kjwl_hsdv51-p1imkz_hrq03t-p1gikw_ho3ljw-p1d0bn_hrgotk-p1biu2_hl4eya-p1bira_',
        '_gid': 'GA1.2.725257540.1514083348',
        'lp_lt_ut': '021fa876ce247b517f560d90d3eb6059',
        'lps': 'http%3A%2F%2Fwww.anjuke.com%2F%7Chttps%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DgsRWoaewpLFwpt3HAjNVTMEmqlFR06kYZ82265g8vTy%26wd%3D%26eqid%3De9f806740001db48000000065a428211',
        'sessid': 'D0458865-F228-5FAC-5CB3-7F3DEFC98A5A',
        'twe': '2',
        'new_session': '0',
        'init_refer': 'https%253A%252F%252Fwww.anjuke.com%252Fsy-city.html',
        '_gat': '1'
    }
    default_delay = 4  # 默认限速

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_city)

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
                yield scrapy.Request(url=new_house_url, callback=self.parse_new_house_urls)
            if used_house_url:
                time.sleep(self.default_delay)  # 限速
                yield scrapy.Request(url=used_house_url, callback=self.parse_used_house_urls)

    # 解析新房页面中各个区/县的url
    def parse_new_house_urls(self, response):
        city = response.xpath("//span[@class='city']/text()").extract_first()
        if city:
            city = city.strip()
        county_nodes = response.xpath("//div[@class='filter']/a")
        if county_nodes:
            for node in county_nodes:
                address = AddressItem()
                address['city'] = city
                county = node.xpath("./text()").extract_first()
                if county:
                    address['county'] = county.strip()
                url = node.xpath("./@href").extract_first()
                if url:
                    time.sleep(self.default_delay)  # 限速
                    yield scrapy.Request(url=url,
                                         callback=self.parse_new_house_list,
                                         meta={'address': address})

    # 解析二手房页面中各个区/县的url
    def parse_used_house_urls(self, response):
        city = response.xpath("//span[@class='city']/text()").extract_first()
        if city:
            city = city.strip()
        county_nodes = response.xpath("//div[class='div-border items-list']/div[1]/span[@class='elems-l']/a")
        if county_nodes:
            for node in county_nodes:
                address = AddressItem()
                address['city'] = city
                county = node.xpath("./text()").extract_first()
                if county:
                    address['county'] = county.strip()
                url = node.xpath("./@href").extract_first()
                if url:
                    time.sleep(self.default_delay)  # 限速
                    yield scrapy.Request(url=url,
                                         callback=self.parse_used_house_list,
                                         meta={"address": address})

    # 解析新房列表中的所有url
    def parse_new_house_list(self, response):
        urls = response.xpath("//div[@class='key-list']/div[@class='item-mod']/@data-link").extract()
        if urls:
            for url in urls:
                yield scrapy.Request(url=url,
                                     callback=self.parse_new_house_homepage,
                                     meta={'address': response.meta['address']})
        # 下一页
        next_page = response.xpath("//a[@class='next-page next-link']/@href").extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_new_house_list,
                                 meta={'address': response.meta['address']})

    # 解析楼盘首页导航栏中“楼盘详情”url
    def parse_new_house_homepage(self, response):
        detail_url = response.xpath("//ul[@class='lp-navtabs clearfix']/li[2]/a/@href").extract_first()
        if detail_url:
            yield scrapy.Request(url=detail_url,
                                 callback=self.parse_new_house_details,
                                 meta={'address': response.meta['address']})

    # 解析楼盘详情页中的详细信息
    def parse_new_house_details(self, response):
        item = HousecrawlerItem()
        address = response.meta['address']
        item['city'] = address['city'].encode('UTF-8')
        item['county'] = address['county'].encode('UTF-8')
        basic_info = response.xpath("//div[@class='can-left']/div[1]/div[@class='can-border']/ul[@class='list']")
        sale_info = response.xpath("//div[@class='can-left']/div[2]/div[@class='can-border']/ul[@class='list']")
        # 基本信息
        if basic_info:
            house_name = basic_info.xpath("./li[1]/div[@class='des']/a/text()").extract_first()
            if house_name:
                item['house_name'] = house_name.strip().encode('UTF-8')
            unit_price = basic_info.xpath("./li[3]/div[@class='des']/span/text()").extract_first()
            if unit_price:
                item['unit_price'] = unit_price.strip()
            total_price = basic_info.xpath("./li[4]/div[@class='des']/span/text()").extract_first()
            if total_price:
                item['total_price'] = total_price.strip()
            house_address = basic_info.xpath("./li[last()]/div[@class='des']/text()").extract_first().strip().encode('UTF-8')
            if house_address:
                item['house_address'] = house_name.strip().encode('UTF-8')
        # 销售信息
        if sale_info:
            down_payment_str = sale_info.xpath("./li[1]/div[@class='des']/text()").extract_first()
            if down_payment_str:
                down_payment_str = down_payment_str.strip()
                item['down_payment'] = re.search(r'\d+.\d+', down_payment_str)
            monthly_payment_str = sale_info.xpath("./li[2]/div[@class='des']/text()").extract_first()
            if monthly_payment_str:
                monthly_payment_str = monthly_payment_str.strip()
                item['monthly_payment'] = re.search(r'\d+.\d+', monthly_payment_str)
            build_year_str = sale_info.xpath("./li[5]/div[@class='des']/text()").extract_first()
            if build_year_str:
                build_year_str = build_year_str.strip()
                item['build_year'] = re.search(r'\d+', build_year_str)
        item['url'] = response.url
        item['crawl_time'] = time.time()
        item['source'] = '安居客'
        item['type'] = 'new'
        print item # 测试用
        return item

    # 解析二手房列表中的所有url
    def parse_used_house_list(self, response):
        urls = response.xpath("//ul[@id='houselist-mod-new']/li[@class='list-item']/div[@class='house-title']/a/@href").exctract()
        if urls:
            for url in urls:
                yield scrapy.Request(url=url,
                                     callback=self.parse_used_house_details,
                                     meta={'address': response.meta['address']})
        next_page = response.xpath("//a[@class='aNxt']/@href").extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_used_house_list,
                                 meta={'address': response.meta['address']})

    # 解析二手房的详细信息
    def parse_used_house_details(self, response):
        item = HousecrawlerItem()
        address = response.meta['address']
        item['city'] = address['city']
        item['county'] = address['county']
        details_info = response.xpath("//div[@class='houseInfoV2-wrap']/div[@class='houseInfoV2-detail clearfix']").extract_first()
        if details_info:
            first_col = details_info.xpath("./div[@class='first-col detail-col']")
            third_col = details_info.xpath("./div[@class='third-col detail-col']")
            if first_col:
                house_name = first_col.xpath("./dl[1]/dd/a/text()").extract_first().strip().encode('UTF-8')
                if house_name:
                    item['house_name'] = house_name.strip().encode('UTF-8')
                house_address_str = first_col.xpath("./dl[2]/dd/p/text()").extract()
                if house_address_str:
                    for str in house_address_str:
                        item['house_address'] = item['house_address'] + str.encode('UTF-8')
                build_year_str = first_col.xpath("./dl[3]/dd/text()").extract_first()
                if build_year_str:
                    build_year_str = build_year_str.strip()
                    item['build_year'] = re.search(r'\d+', build_year_str)
            if third_col:
                unit_price_str = third_col.xpath("./dl[2]/dd/text()").extract_first()
                if unit_price_str:
                    unit_price_str = unit_price_str.strip()
                    item['unit_price'] = re.search(r'\d+', unit_price_str)
                down_payment_str = third_col.xpath("./dl[3]/dd/text()").extract_first()
                if down_payment_str:
                    down_payment_str = down_payment_str.strip()
                    item['down_payment'] = re.search(r'\d+.\d+', down_payment_str)
                monthly_payment_str = third_col.xpath("./dl[4]/dd/sapn/text()").extract_first()
                if monthly_payment_str:
                    monthly_payment_str = monthly_payment_str.strip()
                    item['monthly_payment']  = re.search(r'\d+.\d', monthly_payment_str)
        total_price = response.xpath("//div[@class='basic-info clearfix']/span[@class='light info-tag']/em/text()").extract_first()
        if total_price:
            item['total_price'] = total_price.strip()
        item['url'] = response.url
        item['crawl_time'] = time.time()
        item['source'] = '安居客'
        item['type'] = 'used'
        print item  # 测试用
        return item
