# -*- coding: utf-8 -*-
import MySQLdb

from HouseCrawler.mysqldb.base_table import BaseTable

class ProvinceCity(BaseTable):
    @classmethod
    def select_province_by_city(cls, city=None):
        if city:
            db = cls.get_db()
            cursor = db.cursor()
            sql = "select province from province_city where city=%s"
            result = None
            try:
                cursor.execute(sql, [city])
                result = cursor.fetchone()
            except MySQLdb.Error, e:
                print "Mysql Error:%s" + str(e)
                db.rollback()
            cursor.close()
            db.close()
            if result:
                return result[0]
            else:
                return None
        else:
            return None