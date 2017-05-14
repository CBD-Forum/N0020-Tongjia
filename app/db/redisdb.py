#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import json

from app import redis_store
from app.utils import util

CLASS_TABLE = "class:%s:%s"
CLASS_SET = "classset:%s"

SEPARATOR = '_##'


class RedisMixIn(object):
    def stored_data(self):
        """

        :return:
        :rtype dict
        """
        raise NotImplementedError("must impl!")

    def save_to_redis(self, key, expire=0):
        """
        
        :param key: 
        :param expire: for seconds 
        :return: 
        """
        redis_key = CLASS_TABLE % (type(self).__name__, key)
        if expire != 0:
            redis_store.setex(redis_key, expire, json.dumps(self.stored_data()))
        else:
            redis_store.set(redis_key, json.dumps(self.stored_data()))
        pass

    @classmethod
    def load_from_redis(cls, key, expire=0):
        redis_key = CLASS_TABLE % (cls.__name__, key)
        ret = redis_store.get(redis_key)
        if ret is None:
            return None
        try:
            ins = json.loads(ret)
            if expire != 0:
                redis_store.expire(redis_key, expire)
        except Exception, e:
            print ("load from redis error for %s" % key)
            return None
        return ins

    def remove_from_redis(self, key):
        redis_store.delete(CLASS_TABLE % (type(self).__name__, key))

    @classmethod
    def remove_from_redis_ex(cls, key):
        redis_store.delete(CLASS_TABLE % (cls.__name__, key))

    @classmethod
    def get_count(cls):
        keys = redis_store.keys(CLASS_TABLE % (cls.__name__, "*"))
        if keys is None:
            return 0
        return len(keys)

    pass


class RedisZSetMixIn(RedisMixIn):
    def add_to_set(self, score):
        _id = unicode(util.get_time())
        return redis_store.zadd(CLASS_SET % type(self).__name__, score, SEPARATOR.join((_id, self.to_dict())))

    @classmethod
    def get_from_set(cls, score):
        r = cls.get_all_from_set(score, score)  # list<score, item>
        if r:
            return [i[1] for i in r]  # just get instances not score
        return r  # r is []

    def get_set_score(self):
        _id = unicode(util.get_time())
        return redis_store.zscore(CLASS_SET % type(self).__name__,  # key
                                  SEPARATOR.join((_id, self.to_dict())))  # item

    @classmethod
    def get_all_from_set(cls, min_score=0, max_score=-1, desc=False):
        if desc:
            ret = redis_store.zrevrange(CLASS_SET % cls.__name__, min_score, max_score, withscores=True)
        else:
            ret = redis_store.zrange(CLASS_SET % cls.__name__, min_score, max_score, withscores=True)
        l = list()
        if ret:
            for c, score in ret:
                r = c.split(SEPARATOR, 1)
                if len(r) == 2:
                    try:
                        ins = json.loads(ret)
                        l.append((score, ins))  # (score, item)
                    except Exception, e:
                        print ("load from redis error for score:%s" % score)
        return l

    @classmethod
    def remove_all(cls):
        redis_store.bc_delete(CLASS_SET % cls.__name__)
        pass

    def remove_from_set(self):
        _id = unicode(util.get_time())
        return redis_store.zrem(CLASS_SET % type(self).__name__,  # key
                                SEPARATOR.join((_id, self.to_dict())))  # item

    @classmethod
    def remove_from_set_ex(cls, score):
        return redis_store.zrem(CLASS_SET % cls.__name__,  # key
                                score)  # score

    @classmethod
    def get_min_score_data(cls):
        ret = redis_store.zrangebyscore(CLASS_SET % cls.__name__, '-inf', '+inf', start=0, num=1, withscores=True)
        print ret
        if ret:
            print ret[0][0]
            r = ret[0][0].split(SEPARATOR, 1)
            print r
            if len(r) == 2:
                try:
                    ins = json.loads(r[1])
                    return r[0][1], ins  # (score, data)
                except Exception, e:
                    return None

        return None

    @classmethod
    def get_max_score_data(cls):
        ret = redis_store.zrevrangebyscore(CLASS_SET % cls.__name__, '+inf', '-inf', start=0, num=1, withscores=True)
        print ret
        if ret:
            print ret[0][0]
            r = ret[0][0].split(SEPARATOR, 1)
            print r
            if len(r) == 2:
                try:
                    ins = json.loads(r[1])
                    return ret[0][1], ins  # (score, data)
                except Exception, e:
                    return None
        return None

    @classmethod
    def set_size(cls, smin=-1, smax=-1):
        if smin != -1 and smax != -1 and smin <= smax:
            return redis_store.zcount(CLASS_SET % cls.__name__, smin, smax)
        return redis_store.zcard(CLASS_SET % cls.__name__)

    def to_dict(self):
        d = self.stored_data()
        return json.dumps(d)

    pass


def main():
    pass


if __name__ == '__main__':
    main()
