#!/usr/bin/env python  
# -*- coding: utf-8 -*-
# from flask.ext.mongoalchemy import MongoAlchemy
# from flask.ext.mongoalchemy import BaseQuery
from app import app

# db = MongoAlchemy(app)


from mongoengine import *
connect(app.config['MONGOALCHEMY_DATABASE'])

# class Query(BaseQuery):
#     def getbykid(self, kid):
#         return self.filter(self.type.kid == kid)
#
#     pass


def main():
    pass


if __name__ == '__main__':
    main()
