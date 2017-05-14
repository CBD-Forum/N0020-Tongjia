#!/usr/bin/env python  
# -*- coding: utf-8 -*-

# !/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
import json
from base import BlockChain
from app import app

TX_URL = app.config["BLOCKCHAIN_TX_URL"]
CHAINCODE_ID = app.config["BLOCKCHAIN_TX_CHAINCODE_ID"]


class BlockChainTxMixIn(object):
    @classmethod
    def from_blockchain(cls, txid):
        data = deepcopy(TX_QUERY_DATA)
        data["params"]["ctorMsg"]["function"] = "queryTxInfo"
        data["params"]["ctorMsg"]["args"] = [txid]
        ret = BlockChain.query(TX_URL, data)
        print "qurey:"
        print json.dumps(ret)
        return cls.load_from_dict(ret) if ret is not None else None

    def bc_create(self):
        data = deepcopy(TX_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "create"
        data["params"]["ctorMsg"]["args"] = self.blockchain_create_params()
        # print "++++++++++++"
        # print json.dumps(data)
        # print "+++++++++"
        ret = BlockChain.invoke(TX_URL, data)
        print "+++++++++"
        print ret

    def blockchain_create_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_artificial_check(self, result):
        data = deepcopy(TX_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "artificialCheck"
        data["params"]["ctorMsg"]["args"] = self.blockchain_check_params(result)
        ret = BlockChain.invoke(TX_URL, data)
        print "+++++++++"
        print ret

    def blockchain_check_params(self, result):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_evaluate(self, userid, score):
        data = deepcopy(TX_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "evaluate"
        data["params"]["ctorMsg"]["args"] = self.blockchain_evaluate_params(userid, score)
        ret = BlockChain.invoke(TX_URL, data)
        print "+++++++++"
        print ret

    def blockchain_evaluate_params(self, userid, score):
        raise NotImplementedError("Must impl this func and return a list")

    pass


TX_INVOKE = """
{
"jsonrpc": "2.0",
"method": "invoke",
"params": {
  "type": 1,
  "chaincodeID": {
    "name": "%s"
  },
  "ctorMsg": {
    "function": null,
    "args": [
      
    ]
  },
  "secureContext": "user_type1_0"
},
"id": 0
}
""" % CHAINCODE_ID
TX_INVOKE_DATA = json.loads(TX_INVOKE)

TX_QUERY = """
{
"jsonrpc": "2.0",
"method": "query",
"params": {
  "type": 1,
  "chaincodeID": {
    "name": "%s"
  },
  "ctorMsg": {
    "function": "queryTxInfo",
    "args": [
      
    ]
  },
  "secureContext": "user_type1_0"
},
"id": 0
}
""" % CHAINCODE_ID
TX_QUERY_DATA = json.loads(TX_QUERY)


def main():
    pass


if __name__ == '__main__':
    main()
