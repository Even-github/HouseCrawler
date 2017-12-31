# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import uuid

class HousecrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field() # 编号
    house_name = scrapy.Field() # 楼盘名称
    unit_price = scrapy.Field() # 参考单价
    total_price = scrapy.Field() # 楼盘总价
    down_payment = scrapy.Field() # 首付
    monthly_payment = scrapy.Field() # 月供
    build_year = scrapy.Field() # 建筑年份
    province = scrapy.Field() # 省
    city = scrapy.Field() # 市
    county = scrapy.Field() # 区/县
    house_address = scrapy.Field() # 详细地址
    url = scrapy.Field() # 详情地址
    crawl_time = scrapy.Field() # 爬取时间（时间戳）
    source = scrapy.Field() # 信息来源（网站）
    type = scrapy.Field() # 类型（新房new，二手房used）
    description = scrapy.Field() # 描述

class AddressItem(scrapy.Item):
    city = scrapy.Field() # 市
    county = scrapy.Field() # 区/县

class SpiderDataSourceItem(scrapy.Item):
    id = scrapy.Field()
    source_name = scrapy.Field()
    type = scrapy.Field()
    city = scrapy.Field()
    county = scrapy.Field()
    url = scrapy.Field()
