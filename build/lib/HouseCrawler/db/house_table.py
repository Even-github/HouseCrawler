# -*- coding: utf-8 -*-
import MySQLdb
from HouseCrawler.mysqldb.base_table import BaseTable

class HouseTable(BaseTable):
    @classmethod
    def save_data(cls, data=None):
        if data is not None:
            db = cls.get_db()
            cursor = db.cursor()
            sql = "insert into house " \
                  "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            try:
                cursor.execute(sql, (data['id'],data['house_name'],data['unit_price'],data['total_price'],
                                     data['down_payment'],data['monthly_payment'],data['build_year'],data['province'],
                                     data['city'],data['county'],data['house_address'],data['url'],
                                     data['crawl_time'],data['source'],data['type'],data['description']))
            except MySQLdb.Error, e:
                print "Mysql Error:%s" + str(e)
                db.rollback()
            db.close()
