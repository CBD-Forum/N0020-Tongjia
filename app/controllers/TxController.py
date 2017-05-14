#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from app.modules import Tx
import time


def get_tx(**argv):
    return Tx.objects.filter(**argv).first()  # return None


def get_tx_by_txid(txid):
    return get_tx(id=txid)


def create_tx(userid, jobid):
    tx = Tx(JobID=jobid,
            UserID=userid,
            ApplyTime=unicode(int(time.time())))
    tx.save()
    tx.bc_create()
    return tx


def main():
    pass


if __name__ == '__main__':
    main()
