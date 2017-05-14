#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import app
from .routersutil import *
from app.modules import Tx, UserRole
from app.controllers import TxController, JobController


@app.route('/tx/apply', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def student_apply(userindex):
    data = get_data_from_ajax()
    JobID = data.get("JobID", None)
    if JobID is None:
        abort(400, u"缺少 JobID")

    if JobID in userindex.JobTxMap.keys():
        tx = Tx.from_blockchain(unicode(userindex.JobTxMap[JobID]))
        if tx is not None:
            tx.save()
            print "tx from existed data!"
            return return_data(data=tx.dump_to_dict())

    tx = TxController.create_tx(userindex.UserID, JobID)
    # add tx status re-get
    new_tx = Tx.from_blockchain(unicode(tx.id))
    if new_tx is None:
        abort(403, u"创建 %s 没有成功" % tx.id)
    new_tx.save()

    job = JobController.get_job_by_jobid(jobid=JobID)
    if job is not None:
        job.TotalApplied += 1
        job.save()
        userindex.JobTxMap[JobID] = unicode(new_tx.id)  # {jobid: txid}
        userindex.save()

    return return_data(data=new_tx.dump_to_dict())


@app.route('/tx/student/jobs', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def get_student_txs(userindex):
    if userindex.Role != UserRole.Student:
        abort(403, u"只有学生可以查询")
    l = list()
    for jobid, txid in userindex.JobTxMap.items():
        job = JobController.get_job_by_jobid(jobid)
        # TODO check with front end
        if job is not None:
            d = job.dump_to_dict()
            # TODO wait for check
            txs = d.pop("Txs")
            d["Tx"] = TxController.get_tx_by_txid(txid).dump_to_dict()
            l.append(d)
    l.sort(key=lambda x: x["Tx"]["Time"], reverse=True)

    data = get_data_from_ajax()
    state = data.get("State", None)
    if state is not None:
        try:
            state = int(state)
            if not (0 <= state <= 4):
                abort(400, "State 只能是 0,1,2,3,4")
        except ValueError, e:
            abort(400, "State 只能是数字")
        ret = list()
        for t in l:
            if t["Tx"]['State'] == state:
                ret.append(t)
        return return_data(data=ret)
    return return_data(data=l)


@app.route('/tx/query', methods=['GET', 'POST'])
@allow_cross_domain
def tx_query():
    data = get_data_from_ajax()
    txid = data.get("TxID", None)
    if txid is None:
        abort(400, u"缺少 TxID")

    tx = Tx.from_blockchain(txid)
    if tx is None:
        abort(403, u"没有查找到对应JobID: %s 的兼职信息" % txid)
    tx.save()
    return return_data(data=tx.dump_to_dict())


@app.route('/tx/agency/check', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth
def agency_check(userindex):
    if userindex.Role != UserRole.Agency:
        abort(403, u"只有中介可以检查")
    data = get_data_from_ajax()
    txid = data.get("TxID", None)
    result = data.get("Result", None)
    if txid is None or result is None:
        abort(400, u"缺少 TxID 或 Result")
    # tx = Tx.from_blockchain(txid)
    tx = TxController.get_tx_by_txid(txid)
    if tx is None:
        abort(403, u"提供的tx: %s 不存在" % txid)

    result = unicode(result)
    if result not in [u"1", u"2"]:
        abort(403, u"result only can be: 1 or 2")
    tx.bc_artificial_check(result)
    # lookup
    tx = Tx.from_blockchain(txid)
    tx.save()
    return return_data(data=tx.dump_to_dict())


@app.route('/tx/evaluate', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def evaluate(userindex):
    data = get_data_from_ajax()
    txid = data.get("TxID", None)
    score = data.get("Score", None)
    if txid is None or score is None:
        abort(400, u"缺少 TxID 或 Score")

    try:
        score = int(score)
        if score < 0 or score > 10:
            abort(400, u"评分必须在0-10之间")
    except ValueError, e:
        abort(400, u"评分必须是0-10中的一个数字")

    userid = userindex.UserID
    # tx = Tx.from_blockchain(txid)
    tx = TxController.get_tx_by_txid(txid)
    if tx is None:
        abort(403, u"提供的tx: %s 不存在" % txid)

    tx.bc_evaluate(userid, score)
    # return tx state
    # lookup
    tx = Tx.from_blockchain(txid)
    tx.save()
    return return_data(data=tx.dump_to_dict())
