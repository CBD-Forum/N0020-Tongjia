#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from . import app
from .routersutil import *
from app.modules import JobInfo, UserRole, User
from app.controllers import JobController, UserController


@app.route('/job/all', methods=['GET', 'POST'])
@allow_cross_domain
def get_all_jobs():
    l = JobController.get_all_agency_and_jobs()
    ret = list()
    for i in l:  # i is agencyindex
        count = 0
        name = unicode(i[0])
        score = float(i[1])
        for job in reversed(i[2]):
            if count > 5:
                break
            ret.append({"AgencyName": name, "Score": score, "JobInfo": job})
            count += 1
    return return_data(data=ret)


@app.route('/job/time/all', methods=['GET', 'POST'])
@allow_cross_domain
def get_all_jobs_by_time():
    jobs = JobController.get_all_jobs_by_time()
    ret = list()
    max_count = 20
    max_count = max_count if max_count < len(jobs) else len(jobs)
    for i in range(max_count):
        job = jobs[i]
        print job.PublishTime
        userindex = UserController.get_userindex_byuserid(job.UserID)
        if userindex is not None:
            ret.append({"AgencyName": userindex.AgencyName, "Score": userindex.CurrentCreditScore,
                        "JobInfo": job.dump_to_dict()})

    return return_data(data=ret)


@app.route('/job/agency/publish', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def publish_job(userindex):
    if userindex.Role != UserRole.Agency:
        abort(403, u"只有中介能发布信息")
    data = get_data_from_ajax()

    check_list = list()
    title = data.get("Title", None)
    jobtime = data.get("JobTime", None)
    place = data.get("Place", None)
    salary = data.get("Salary", None)
    day = data.get("Day", None)
    demand = data.get("Demand", None)

    check_list.append(title)
    check_list.append(jobtime)
    check_list.append(place)
    check_list.append(salary)
    check_list.append(day)
    check_list.append(demand)

    if check_list.count(None):
        abort(400, u"缺少参数%d" % check_list.index(None))

    try:
        s = int(salary)
        if s <= 0 or s > 65535:
            abort(400, u"Salary 设置不合理")
    except ValueError, e:
        abort(400, u"Salary 必须是一个整数")

    job = JobController.create_jobinfo(userindex, title, jobtime, place, salary, day, demand)
    userindex.JobTxMap[unicode(job.id)] = ""
    userindex.save()
    return return_data(data=job.dump_to_dict())


@app.route('/job/agency/jobs', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth
def get_agency_jobs(userindex):
    """
    from cache
    :param userindex: 
    :return: 
    """
    data = get_data_from_ajax()
    if userindex.Role != UserRole.Agency:
        abort(403, u"只有中介可以查询")
    l = list()

    state = data.get("State", None)
    if state is not None:
        try:
            state = int(state)
            if not (0 <= state <= 4):
                abort(400, "State 只能是 0,1,2,3,4")
        except ValueError, e:
            abort(400, "State 只能是数字")

    for jobid in userindex.JobTxMap.keys():
        job = JobController.get_job_by_jobid(jobid)
        if job is not None:
            d = job.dump_to_dict()
            if state is not None:
                tx_list = list()
                txs = d["Txs"]
                for t in txs:
                    if t['State'] == state:
                        tx_list.append(t)
                tx_list.sort(key=lambda x: x["Time"], reverse=True)
                d["Txs"] = tx_list

            l.append(d)
    l.sort(key=lambda x: x["Time"], reverse=True)
    return return_data(data=l)


@app.route('/job/query', methods=['GET', 'POST'])
@allow_cross_domain
def job_query():
    data = get_data_from_ajax()
    jobid = data.get("JobID", None)
    if jobid is None:
        abort(400, "缺少 JobID")

    job = JobInfo.from_blockchain(jobid)
    if job is None:
        abort(403, u"没有查找到对应JobID: %s 的兼职信息" % jobid)
    # print type(job.id)
    job.save()

    d = job.dump_to_dict()
    username = data.get("username", None)
    if username is None:
        username = data.get("Username", None)
    if username is not None:
        userindex = UserController.get_userindex_byname(username)
        if userindex is not None:
            if jobid in userindex.JobTxMap.keys():
                d["IsApplied"] = True
            else:
                d["IsApplied"] = False

    state = data.get("State", None)
    if state is not None:
        try:
            state = int(state)
            if not (0 <= state <= 4):
                abort(400, "State 只能是 0,1,2,3,4")
        except ValueError, e:
            abort(400, "State 只能是数字")
        txs = d["Txs"]
        l = list()
        for t in txs:
            if t['State'] == state:
                l.append(t)
        d["Txs"] = l

    return return_data(data=d)


############################
@app.route('/job/loadbctest', methods=['GET', 'POST'])
def load_bc_test():
    job = JobInfo.from_blockchain('590e9e4ee588d600d4fb0aaf')
    # print type(job.id)
    return return_data(data=job.dump_to_dict())


@app.route('/job/loadtest', methods=['GET', 'POST'])
def loadtest_job():
    s = """{
    "JobDetail": {
      "Day": 0, 
      "Demand": "", 
      "JobTime": "", 
      "Place": "", 
      "Salary": 0
    }, 
    "JobID": "085308f0-38f8-40a3-b631-7cb33811a985", 
    "TotalApplied": "123", 
    "TotalHired": "123", 
    "TotalSettled": "123", 
    "TotalWaitCheck": "123", 
    "Txs": [
      "123", 
      "123"
    ]
  }"""
    data = json.loads(s)
    ins = JobInfo.load_from_dict(data)
    return return_data(data=ins.dump_to_dict())

# def main():
#     pass
#
#
# if __name__ == '__main__':
#     main()
