#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from flask import Flask, session
import os
import logging
from flask_redis import FlaskRedis


def create_app():
    inner_app = Flask(__name__, instance_relative_config=True)
    # 加载配置  从根项目下的config.py加载
    inner_app.config.from_object('config')
    # 加载配置 从 instance/config.py 加载，需要在Flask(__name__, instance_relative_config=True(加这个参数))，可覆盖上面配置
    inner_app.config.from_pyfile('config.py')
    # log
    handler = __create_log_handler(inner_app)
    inner_app.logger.addHandler(handler)
    # init redis
    redis_store = FlaskRedis(inner_app)
    return inner_app, redis_store


def __create_log_handler(app):
    path = os.path.realpath(__file__)
    log_path = os.path.dirname(path) + '/../logs/flask.log'
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')

    if app.debug:
        handler = logging.FileHandler(log_path, mode='w', encoding='UTF-8')
    else:
        handler = logging.FileHandler(log_path, mode='a', encoding='UTF-8')
        handler.setLevel(logging.ERROR)

    handler.setFormatter(logging_format)
    return handler


app, redis_store = create_app()
logger = app.logger

# import redis
# redisdb = redis.StrictRedis(host='localhost', port=6379, db=0)
# redisdb.zrangebyscore()

from app.routes import *
