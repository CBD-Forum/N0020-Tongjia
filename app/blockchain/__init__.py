#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import requests
import json
from copy import deepcopy
import traceback
from hyperledger.client import Client
from .. import app

# BLOCKCHAIN_URL = app.config['BLOCKCHAIN_URL']


# 适合用于区块信息展示
# blockchain_client = Client(base_url=BLOCKCHAIN_URL)
JOBINFO_URL = app.config["BLOCKCHAIN_JOBINFO_URL"]


def test_conn():
    r = requests.get(JOBINFO_URL)
    return r


def main():
    pass


if __name__ == '__main__':
    main()
