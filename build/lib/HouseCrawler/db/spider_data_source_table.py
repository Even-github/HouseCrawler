# -*- coding: utf-8 -*-

from HouseCrawler.db.base_table import BaseTable

class SpiderDataSourceTable(BaseTable):
    @classmethod
    def save_data(cls, data=None):
        if data is not None:
            db = cls.get_db()
            cursor = db.cursor()
            sql = "select count(id) as amount from spider_data_source " \
                  "where source_name=%s and type=%s and city=%s and county=%s"
            cursor.execute(sql, (data['source_name'], data['type'], data['city'], data['county']))
            amount = cursor.fetchone()
            try:
                if int(amount[0]) > 0:
                    sql = "update spider_data_source set url=%s " \
                          "where source_name=%s and type=%s and city=%s"
                    cursor.execute(sql, (data['url'], data['source_name'], data['type'], data['city']))
                    print sql
                else:
                    sql = "insert into spider_data_source values " \
                          "(%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (data['id'], data['source_name'], data['type'], data['city'], data['county'], data['url']))
                    print sql
            except:
                db.rollback()
            cursor.close()
            db.close()

    @classmethod
    def select_url_by_fields(cls, condition):
        if condition:
            db = cls.get_db()
            cursor = db.cursor()
            sql = "select url from spider_data_source " \
                  "where source_name=%s and " \
                  "type=%s and city=%s and county=%s"
            cursor.execute(sql, (condition['source_name'], condition['type'], condition['city'], condition['county']))
            result = cursor.fetchone()
            url = None
            if result:
                url = result[0]
            cursor.close()
            db.close()
            return url

