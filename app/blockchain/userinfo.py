#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from copy import deepcopy
import json
from base import BlockChain
from app import app

USERINFO_URL = app.config["BLOCKCHAIN_USERINFO_URL"]
CHAINCODE_ID = app.config["BLOCKCHAIN_USERINFO_CHAINCODE_ID"]


class BlockChainUserInfoMixIn(object):
    @classmethod
    def from_blockchain(cls, userid):
        data = deepcopy(USERINFO_QUERY_DATA)
        data["params"]["ctorMsg"]["function"] = "queryUserInfo"
        data["params"]["ctorMsg"]["args"] = [userid]
        ret = BlockChain.query(USERINFO_URL, data)
        print '+++++++++'
        print ret
        print '+++++++++'
        return cls.load_from_dict(ret) if ret is not None else None

    def bc_create(self):
        data = deepcopy(USERINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "add"
        data["params"]["ctorMsg"]["args"] = self.blockchain_create_params()
        # print json.dumps(data)
        r = BlockChain.invoke(USERINFO_URL, data)
        # print r.text

    def blockchain_create_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_update(self):
        data = deepcopy(USERINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "edit"
        data["params"]["ctorMsg"]["args"] = self.blockchain_update_params()
        BlockChain.invoke(USERINFO_URL, data)

    def blockchain_update_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_delete(self):
        data = deepcopy(USERINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "delete"
        data["params"]["ctorMsg"]["args"] = self.blockchain_delete_params()
        BlockChain.invoke(USERINFO_URL, data)

    def blockchain_delete_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    pass


USERINFO_INVOKE = """
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
USERINFO_INVOKE_DATA = json.loads(USERINFO_INVOKE)

USERINFO_QUERY = """
{
  "jsonrpc": "2.0",
  "method": "query",
  "params": {
    "type": 1,
    "chaincodeID": {
      "name": "%s"
    },
    "ctorMsg": {
      "function": "queryUserInfo",
      "args": [
        
      ]
    },
    "secureContext": "user_type1_0"
  },
  "id": 0
}
""" % CHAINCODE_ID
USERINFO_QUERY_DATA = json.loads(USERINFO_QUERY)


def main():
    pass


if __name__ == '__main__':
    main()
