#!/usr/bin/python
# -*- coding: utf-8 -*-

# mysql

DEBUG = True
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

GONGXIANGDANCHE_TOKEN = ''

TRY_REQ = True

REDIS_URL = "redis://:@localhost:6379/0"
REDIS_QUEUE_KEY = "my_queue"

MONGOALCHEMY_DATABASE = 'library'
MONGOALCHEMY_SERVER_AUTH = False

RUN_IN_PYTHON_SERVER = False  # False for nginx server and True for command `python manage.py runserver -h 0.0.0.0`

BLOCKCHAIN_USERINFO_URL = "https://a6377d73838047d39f8527f035520915-vp0.us.blockchain.ibm.com:5002/chaincode"
BLOCKCHAIN_TX_URL = "https://a6377d73838047d39f8527f035520915-vp0.us.blockchain.ibm.com:5002/chaincode"
BLOCKCHAIN_JOBINFO_URL = "https://a6377d73838047d39f8527f035520915-vp0.us.blockchain.ibm.com:5002/chaincode"

BLOCKCHAIN_USERINFO_CHAINCODE_ID = "9d29747f0b642ed65f481fbc1132d518834b3099671ad5d86feb8609202197f26cefcca348942ce9facdbe8312b5d7ee5598a6d9522c34ae9755720c1176a598"
BLOCKCHAIN_JOBINFO_CHAINCODE_ID = "7147861cb80f5447b0ee974bc917935cc8f65bd89a271095af7e0f7cb8184a7dccdbb93a43fce11d24c7532743c7d22c0fa68c6f6bbc29bb8a92f2e98b2d92ae"
BLOCKCHAIN_TX_CHAINCODE_ID = "3e960549e21165e0a0a03087dc9745436644cb77876ec324949048f7486018cf71f92f30234358c487d7374a7e8ab57156bfec0a2df37cf864f4b2c126716ece"


def main():
    pass


if __name__ == '__main__':
    main()
