#!/usr/bin/env python
# -*- coding: utf-8 -*-

# !/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
import json
from base import BlockChain
from app import app

JOBINFO_URL = app.config["BLOCKCHAIN_JOBINFO_URL"]
CHAINCODE_ID = app.config["BLOCKCHAIN_JOBINFO_CHAINCODE_ID"]


class BlockChainJobInfoMixIn(object):
    @classmethod
    def from_blockchain(cls, jobid):
        data = deepcopy(TX_QUERY_DATA)
        data["params"]["ctorMsg"]["function"] = "queryJobInfo"
        data["params"]["ctorMsg"]["args"] = [jobid]
        ret = BlockChain.query(JOBINFO_URL, data)
        print ret
        return cls.load_from_dict(ret) if ret is not None else None

    def bc_create(self):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "add"
        data["params"]["ctorMsg"]["args"] = self.blockchain_create_params()
        # print "++++++++"
        # print data["params"]["ctorMsg"]["args"]
        # print "++++++++"
        r = BlockChain.invoke(JOBINFO_URL, data)
        print json.dumps(data)
        print r

    def blockchain_create_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_update(self):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "edit"
        data["params"]["ctorMsg"]["args"] = self.blockchain_update_params()
        BlockChain.invoke(JOBINFO_URL, data)

    def blockchain_update_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_delete(self):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "delete"
        data["params"]["ctorMsg"]["args"] = self.blockchain_delete_params()
        BlockChain.invoke(JOBINFO_URL, data)

    def blockchain_delete_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_add_tx(self, txid):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "addTX"
        data["params"]["ctorMsg"]["args"] = self.blockchain_addtx_params(txid)
        BlockChain.invoke(JOBINFO_URL, data)

    def blockchain_addtx_params(self, txid):
        raise NotImplementedError("Must impl this func and return a list")

    def bc_add_total_applied(self):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "addTotalApplied"
        data["params"]["ctorMsg"]["args"] = self.blockchain_jobrelated_params()
        BlockChain.invoke(JOBINFO_URL, data)

    def bc_add_total_wait_check(self):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "addTotalWaitCheck"
        data["params"]["ctorMsg"]["args"] = self.blockchain_jobrelated_params()
        BlockChain.invoke(JOBINFO_URL, data)

    def bc_add_total_hired(self):
        data = deepcopy(JOBINFO_INVOKE_DATA)
        data["params"]["ctorMsg"]["function"] = "addTotalHired"
        data["params"]["ctorMsg"]["args"] = self.blockchain_jobrelated_params()
        BlockChain.invoke(JOBINFO_URL, data)

    # def bc_add_total_settled(self):
    #     data = deepcopy(JOBINFO_INVOKE_DATA)
    #     data["params"]["ctorMsg"]["function"] = "addTotalSettled"
    #     data["params"]["ctorMsg"]["args"] = self.blockchain_jobrelated_params()
    #     BlockChain.invoke(JOBINFO_URL, data)

    def blockchain_jobrelated_params(self):
        raise NotImplementedError("Must impl this func and return a list")

    pass


JOBINFO_INVOKE = """
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
JOBINFO_INVOKE_DATA = json.loads(JOBINFO_INVOKE)

JOBINFO_QUERY = """
{
"jsonrpc": "2.0",
"method": "query",
"params": {
  "type": 1,
  "chaincodeID": {
    "name": "%s"
  },
  "ctorMsg": {
    "function": "queryJobInfo",
    "args": [
      
    ]
  },
  "secureContext": "user_type1_0"
},
"id": 0
}
""" % CHAINCODE_ID
TX_QUERY_DATA = json.loads(JOBINFO_QUERY)


def main():
    pass


if __name__ == '__main__':
    main()
