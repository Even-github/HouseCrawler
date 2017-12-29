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
            string = re.search(r'\d+.\d', string)
            if string:
                return string.group()
            else:
                return None
        else:
            return None