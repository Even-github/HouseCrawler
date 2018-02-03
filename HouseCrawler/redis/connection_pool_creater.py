# -*- coding: utf-8 -*-
import redis

class ConnectionPoolCreater(object):
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)

    @classmethod
    def get_pool(cls):
        return cls.pool
