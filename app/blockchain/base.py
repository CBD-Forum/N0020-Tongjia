#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import json
import requests
import traceback
from flask import abort


class BlockChain(object):
    # def to_blockchain(self, func, **params):
    #     # self.dump_to_dict()
    #     raise NotImplementedError("Must impl this func and return a list")

    # @classmethod
    # def from_blockchain(cls):
    #     # TODO retrieve from blockchain
    #     data = {}
    #     bcid = ""
    #     return cls.load_from_dict(data, bcid)

    @staticmethod
    def post(url, data):
        try:
            r = requests.post(url, json=data)
            data = r.json()
            print data
            if 'result' not in data:
                print "blockchain access return error!"
                return None
            return data['result'] if data['result']['status'] == 'OK' else None
        except ValueError, e:
            print "json parse error!"
            print e
            traceback.print_exc()
            abort(500, u"blockchain 返回数据异常，无法被json解析")
            return None
        except Exception, e:
            print "request error!"
            print e
            traceback.print_exc()
            abort(500, u"访问 blockchain 异常")
            return None

    @staticmethod
    def invoke(url, data):
        return BlockChain.post(url, data)

    @staticmethod
    def query(url, data):
        r = BlockChain.post(url, data)
        if r is None:
            return None
        try:
            # print json.loads(r['message'])
            return json.loads(r['message'])
        except Exception, e:
            print "json parse error for message!"
            print e
            traceback.print_exc()
            return None

    pass


def main():
    pass


if __name__ == '__main__':
    main()
