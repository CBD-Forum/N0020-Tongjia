#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import json
import traceback
from bson import ObjectId


def json_wrapper(obj, error=0, msg='', str_type=False):
    d = {'err': error, 'msg': msg, 'data': obj}
    if str_type:
        return json.dumps(d)
    else:
        return d


def parse_json(json_str):
    try:
        return json.loads(json_str)
    except:
        print "json decoded failed for %s" % json_str
        return None


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return unicode(o)
        return json.JSONEncoder.default(self, o)


def to_json(data):
    try:
        return json.dumps(data, cls=JSONEncoder)
    except Exception, e:
        print "wrong in dumps data to json: %s" % e.message
        traceback.print_exc()


def main():
    pass


if __name__ == '__main__':
    main()
