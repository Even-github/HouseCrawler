# -*- coding: utf-8 -*-
import re
"""
字符串处理工具
"""
class StringUtil(object):
    # 从字符串中获取第一个整数
    @classmethod
    def get_first_int_from_string(cls, string):
        if string:
            string = re.sub(r'\s', '', string)
            string = re.search(r'\d+', string)
            if string:
                return string.group()
            else:
                return None
        else:
            return None

    # 从字符串中获取第一个浮点数
    @classmethod
    def get_first_float_from_string(cls, string):
        if string:
            string = re.sub(r'\s', '', string)
            string = re.search(r'\d+.\d+', string)
            if string:
                return string.group()
            else:
                return None
        else:
            return None

    # 从字符传中获取第一个数字
    @classmethod
    def get_first_number_from_string(cls, string):
        if string:
            string = re.sub(r'\s', '', string)
            num = re.search(r'\d+.\d+', string)
            if num:
                return num.group()
            else:
                num = re.search(r'\d+', string)
                if num:
                    return num.group()
                else:
                    return None
        else:
            return None

    # 从字符串中获取第一个年份
    @classmethod
    def get_first_year_from_string(cls, string):
        if string:
            string = re.sub(r'\s', '', string)
            string = re.search(r'\d\d\d\d', string)
            if string:
                return string.group()
            else:
                return None
        else:
            return None

    # 获取以.com结尾的url中的根目录
    @classmethod
    def get_com_url_root(cls, url):
        if url:
            url = re.sub(r'.com(\S)*', '.com', url)
            return url
        else:
            return None

    # 获取url中的当前目录名，如https://bj.fang.lianjia.com/loupan/chaoyang/pg3/#chaoyang 中的chaoyang
    @classmethod
    def get_url_current_catalog(cls, url):
        if url:
            catalog_obj = re.search(r'((\w)*/)$', url)
            if catalog_obj:
                return re.sub(r'/', '', catalog_obj.group())
            else:
                return None
        else:
            return None

    # 获取单位中的是否包含“套”字
    @classmethod
    def container_tao(cls, string):
        if string:
            tao = re.search(u'套', string)
            if tao:
                return True
            else:
                return False
        else:
            return False