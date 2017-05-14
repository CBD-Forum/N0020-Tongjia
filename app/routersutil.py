#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import json
from functools import wraps
from flask import request, abort, jsonify, render_template, make_response

from app.utils import jsonutil
from app.controllers.UserController import get_userindex_bytoken, get_userindex_byname


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' \
        # and \
    # request.accept_mimetypes[best] > \
    # request.accept_mimetypes['text/html']


def return_data(html=None, data=None, code=0, msg=''):
    if data is None:
        data = dict()
    if html is None or request_wants_json():
        return jsonify(jsonutil.json_wrapper(data, code, msg))
    if not isinstance(data, dict):
        raise RuntimeError("data must be a dict")
    if code == 0:
        code = 200
    return render_template(html, **data), code


def get_data_from_ajax(noabort=False):
    data = dict()
    try:
        if request.data:
            data.update(json.loads(request.data))
        data.update(dict(request.args.items()))
        data.update(request.form.items())
        # data.update(request.data)
    except Exception, e:
        print e.message
        if not noabort:
            abort(400, u'post 数据体为空或不是合法json')
        data.update(request.args.items())
        data.update(request.form.items())
        return data
    return data if type(data) == dict else {}


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun


def check_auth(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        params = dict(request.args.items())  # .items()
        # 后门
        username = params.get('username', None)
        if username is not None:
            userindex = get_userindex_byname(username)
            if userindex is not None:
                return fun(*args, userindex=userindex, **kwargs)

        token = params.get('token', None)
        if token is None:
            abort(401, u"can't find token!")
        userindex = get_userindex_bytoken(token)
        if userindex is None:
            abort(400, u"token is invalid or user is not exist!")
        return fun(*args, userindex=userindex, **kwargs)

    return wrapper_fun


def check_auth_ext(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        params = dict(request.args.items())  # .items()
        # 后门
        username = params.get('username', None)
        if username is not None:
            userindex = get_userindex_byname(username)
            if userindex is not None:
                if userindex.UserID == '':
                    abort(403, u"need to complete personal info first!")
                return fun(*args, userindex=userindex, **kwargs)

        token = params.get('token', None)
        if token is None:
            abort(401, u"can't find token!")
        userindex = get_userindex_bytoken(token)
        if userindex is None:
            abort(400, u"token is invalid or user is not exist!")
        if userindex.UserID == '':
            abort(403, u"need to complete personal info first!")
        return fun(*args, userindex=userindex, **kwargs)

    return wrapper_fun


def main():
    pass


if __name__ == '__main__':
    main()
