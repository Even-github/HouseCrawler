# -*- coding: utf-8 -*-
import MySQLdb

class BaseTable(object):
    @classmethod
    def get_db(self):
        db = MySQLdb.connect(host='localhost',
                             port=3306,
                             db='house_crawl',
                             user='root',
                             passwd='abc123',
                             charset='utf8')
        db.autocommit(on='True')
        return db