#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask import request, Flask, jsonify, render_template, redirect, url_for, flash, abort, send_from_directory, \
    Response, session

from . import app
from .routersutil import *


@app.errorhandler(500)
def inner_error(e):
    msg = e.description
    if request_wants_json():
        return jsonify(jsonutil.json_wrapper(None, 500, msg)), 500
    return "inner error!<br/>%s" % msg, 500


@app.errorhandler(400)
def params_error(e):
    msg = e.description
    if msg == -1:
        msg = u"不允许访问"
    return jsonify(jsonutil.json_wrapper(None, 400, msg)), 400


@app.errorhandler(401)
def need_login(e):
    msg = e.description
    if msg == -1:
        msg = u"身份过期或未登录"
    return jsonify(jsonutil.json_wrapper(None, 401, msg)), 401


@app.errorhandler(403)
def forbid(e):
    msg = e.description
    if msg == -1:
        msg = u"不允许访问"
    return jsonify(jsonutil.json_wrapper(None, 403, msg)), 403


@app.errorhandler(404)
def page_not_found(e):
    msg = e.description
    if msg == -1:
        msg = u"路径错误或没有该资源"
    if request_wants_json():
        return jsonify(jsonutil.json_wrapper(None, 404, msg)), 404
    return render_template('404.html', msg=msg), 404


@app.route('/', methods=['GET', 'POST'])
@allow_cross_domain
def index_redirect():
    return redirect('index.html')


@app.route('/index', methods=['GET', 'POST'])
@allow_cross_domain
def index():
    return render_template('index.html')


@app.route('/index/second', methods=['GET', 'POST'])
@allow_cross_domain
def index2():
    return "123"


@app.route('/fxck', methods=['get', 'post'])
@allow_cross_domain
def fxck():
    return_data(None, {"12": 1})
    return unicode(request.data)
    pass


# add other routers
from .routersuser import *
from .routerstxs import *
from .routersjobs import *


@app.route('/mockdata', methods=['post'])
@allow_cross_domain
def mock_data():
    data = get_data_from_ajax()
    key = data.get("key")
    if key != "motherfxcker":
        abort(403, "key is not valid!")

    # create user
    # student Li
    username = u'Li'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Student
    li_userindex = UserController.create_userindex(username, password, role)
    li_userindex.IDNo = u"53**************11"
    li_userindex.RealName = u"李某"
    li_userindex.Gender = 0
    li_userindex.Tele = u"151********"
    li_userindex.School = u"同济大学"
    li_userindex.StuID = u"1252***"
    li_user = UserController.create_user(li_userindex)

    # student Zhou
    username = u'Zhou'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Student
    zhou_userindex = UserController.create_userindex(username, password, role)
    zhou_userindex.IDNo = u"36**************13"
    zhou_userindex.RealName = u"周某"
    zhou_userindex.Gender = 0
    zhou_userindex.Tele = u"181********"
    zhou_userindex.School = u"同济大学 嘉定校区"
    zhou_userindex.StuID = u"1200***"
    zhou_user = UserController.create_user(zhou_userindex)

    # agency
    # TongjiAgency
    username = u'TongjiAgency'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Agency
    tj_ag_userindex = UserController.create_userindex(username, password, role)
    tj_ag_userindex.IDNo = u"35**************13"
    tj_ag_userindex.RealName = u"周xx"
    tj_ag_userindex.Gender = 0
    tj_ag_userindex.Tele = u"181********"
    tj_ag_userindex.AgencyName = u"同济兼嘉"
    tj_ag_user = UserController.create_user(tj_ag_userindex)
    # ZhouAgency
    username = u'ZhouAgency'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Agency
    zhou_ag_userindex = UserController.create_userindex(username, password, role)
    zhou_ag_userindex.IDNo = u"25**************13"
    zhou_ag_userindex.RealName = u"周xx"
    zhou_ag_userindex.Gender = 0
    zhou_ag_userindex.Tele = u"181********"
    zhou_ag_userindex.AgencyName = u"周氏中介"
    zhou_ag_user = UserController.create_user(zhou_ag_userindex)
    # HuangAgency
    username = u'HuangAgency'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Agency
    huang_ag_userindex = UserController.create_userindex(username, password, role)
    huang_ag_userindex.IDNo = u"45**************13"
    huang_ag_userindex.RealName = u"黄xx"
    huang_ag_userindex.Gender = 0
    huang_ag_userindex.Tele = u"171********"
    huang_ag_userindex.AgencyName = u"黄氏中介"
    huang_ag_user = UserController.create_user(huang_ag_userindex)
    # JinAgency
    username = u'JinAgency'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Agency
    jin_ag_userindex = UserController.create_userindex(username, password, role)
    jin_ag_userindex.IDNo = u"53**************13"
    jin_ag_userindex.RealName = u"金xx"
    jin_ag_userindex.Gender = 0
    jin_ag_userindex.Tele = u"131********"
    jin_ag_userindex.AgencyName = u"金氏中介"
    jin_ag_user = UserController.create_user(jin_ag_userindex)
    # Zhen
    username = u'ZhenAgency'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Agency
    zhen_ag_userindex = UserController.create_userindex(username, password, role)
    zhen_ag_userindex.IDNo = u"13**************13"
    zhen_ag_userindex.RealName = u"郑xx"
    zhen_ag_userindex.Gender = 0
    zhen_ag_userindex.Tele = u"152********"
    zhen_ag_userindex.AgencyName = u"郑氏中介"
    zhen_ag_user = UserController.create_user(zhen_ag_userindex)
    # Wu
    username = u'WuAgency'
    password = hashutil.hash_md5('123qwe')
    role = UserRole.Agency
    wu_ag_userindex = UserController.create_userindex(username, password, role)
    wu_ag_userindex.IDNo = u"13**************13"
    wu_ag_userindex.RealName = u"吴xx"
    wu_ag_userindex.Gender = 0
    wu_ag_userindex.Tele = u"183********"
    wu_ag_userindex.AgencyName = u"吴氏中介"
    wu_ag_userindex.save()
    wu_ag_user = UserController.create_user(wu_ag_userindex)
    #############################################################
    # jobs
    # 1
    title = u"上海房车露营展览会志愿者"
    jobtime = u"8h"
    place = u"上海汽车会展中心"
    salary = u"130"
    day = u"每天"
    demand = u"130元每天，包饭，要求人员认真负责。"
    job1 = JobController.create_jobinfo(zhou_ag_userindex, title, jobtime, place, salary, day, demand)
    zhou_ag_userindex.JobTxMap[unicode(job1.id)] = ""
    zhou_ag_userindex.save()
    # 2
    title = u"家教"
    jobtime = u"2H"
    place = u"学生家中"
    salary = u"130"
    day = u"一周1-2次"
    demand = u"教学科目有水平，认真负责"
    job2 = JobController.create_jobinfo(zhou_ag_userindex, title, jobtime, place, salary, day, demand)
    zhou_ag_userindex.JobTxMap[unicode(job2.id)] = ""
    zhou_ag_userindex.save()
    # 3
    title = u"托班代课"
    jobtime = u"8H"
    place = u"安亭一处辅导班中"
    salary = u"180"
    day = u"1天"
    demand = u"教学科目有水平，认真负责"
    job3 = JobController.create_jobinfo(zhou_ag_userindex, title, jobtime, place, salary, day, demand)
    zhou_ag_userindex.JobTxMap[unicode(job3.id)] = ""
    zhou_ag_userindex.save()

    # 4
    title = u"充场"
    jobtime = u"2H"
    place = u"同济嘉定校区"
    salary = u"40"
    day = u"1天"
    demand = u"无"
    job4 = JobController.create_jobinfo(huang_ag_userindex, title, jobtime, place, salary, day, demand)
    huang_ag_userindex.JobTxMap[unicode(job4.id)] = ""
    huang_ag_userindex.save()
    # 5
    title = u"摄像"
    jobtime = u"8H:30M"
    place = u"同济嘉定校区"
    salary = u"700"
    day = u"1天"
    demand = u"有专业摄影机器，有摄影经验"
    job5 = JobController.create_jobinfo(huang_ag_userindex, title, jobtime, place, salary, day, demand)
    huang_ag_userindex.JobTxMap[unicode(job5.id)] = ""
    huang_ag_userindex.save()
    # 6
    title = u"F1大奖赛上海站工作人员"
    jobtime = u"8H"
    place = u"上海赛车场水景广场"
    salary = u"120"
    day = u"3天"
    demand = u"120每天/包饭"
    job6 = JobController.create_jobinfo(huang_ag_userindex, title, jobtime, place, salary, day, demand)
    huang_ag_userindex.JobTxMap[unicode(job6.id)] = ""
    huang_ag_userindex.save()

    # 7
    title = u"陆家嘴正大广场促销员"
    jobtime = u"9H"
    place = u"陆家嘴正大广场"
    salary = u"180"
    day = u"5天"
    demand = u"180+提成，要求身高165mm以上的女生"
    job7 = JobController.create_jobinfo(jin_ag_userindex, title, jobtime, place, salary, day, demand)
    jin_ag_userindex.JobTxMap[unicode(job7.id)] = ""
    jin_ag_userindex.save()
    # 8
    title = u"微软宣讲会支持"
    jobtime = u"4H"
    place = u"同济嘉定校区"
    salary = u"100"
    day = u"1天"
    demand = u"100+包饭"
    job8 = JobController.create_jobinfo(jin_ag_userindex, title, jobtime, place, salary, day, demand)
    jin_ag_userindex.JobTxMap[unicode(job8.id)] = ""
    jin_ag_userindex.save()
    # 9
    title = u"京东开学季路演支持"
    jobtime = u"8H"
    place = u"同济嘉定校区"
    salary = u"130"
    day = u"1天"
    demand = u"无"
    job9 = JobController.create_jobinfo(jin_ag_userindex, title, jobtime, place, salary, day, demand)
    jin_ag_userindex.JobTxMap[unicode(job9.id)] = ""
    jin_ag_userindex.save()
    # 10
    title = u"京东开学季传单发放"
    jobtime = u"2H"
    place = u"同济嘉定校区"
    salary = u"60"
    day = u"1天"
    demand = u"无"
    job10 = JobController.create_jobinfo(jin_ag_userindex, title, jobtime, place, salary, day, demand)
    jin_ag_userindex.JobTxMap[unicode(job10.id)] = ""
    jin_ag_userindex.save()

    # 11
    title = u"EVCARD问卷调查志愿者"
    jobtime = u"5-6H"
    place = u"上海市"
    salary = u"170"
    day = u"30天"
    demand = u"会开车且注册过EVCARD，完成指定任务"
    job11 = JobController.create_jobinfo(zhen_ag_userindex, title, jobtime, place, salary, day, demand)
    zhen_ag_userindex.JobTxMap[unicode(job11.id)] = ""
    zhen_ag_userindex.save()
    # 12
    title = u"新阳辅导团队"
    jobtime = u"3H"
    place = u"黄渡新阳辅导中心"
    salary = u"110"
    day = u"至少一学期"
    demand = u"110包饭，认真负责"
    job12 = JobController.create_jobinfo(zhen_ag_userindex, title, jobtime, place, salary, day, demand)
    zhen_ag_userindex.JobTxMap[unicode(job12.id)] = ""
    zhen_ag_userindex.save()
    # 13
    title = u"支点教育助教"
    jobtime = u"8H: 30M"
    place = u"嘉定区天祝路嘉鼎国际大厦"
    salary = u"180"
    day = u"180天"
    demand = u"解题能力强，思路清晰，思维灵活，工作踏实"
    job13 = JobController.create_jobinfo(zhen_ag_userindex, title, jobtime, place, salary, day, demand)
    zhen_ag_userindex.JobTxMap[unicode(job13.id)] = ""
    zhen_ag_userindex.save()

    # 14
    title = u"晋元高级中学教师运动会"
    jobtime = u"3H"
    place = u"晋元高级中学"
    salary = u"130"
    day = u"1天"
    demand = u"无"
    job14 = JobController.create_jobinfo(zhen_ag_userindex, title, jobtime, place, salary, day, demand)
    zhen_ag_userindex.JobTxMap[unicode(job14.id)] = ""
    zhen_ag_userindex.save()
    # 15
    title = u"元旦赛场迎新跑"
    jobtime = u"8H"
    place = u"上海赛车场"
    salary = u"120"
    day = u"1天"
    demand = u"120包饭，仅限女生报名"
    job15 = JobController.create_jobinfo(zhen_ag_userindex, title, jobtime, place, salary, day, demand)
    zhen_ag_userindex.JobTxMap[unicode(job15.id)] = ""
    zhen_ag_userindex.save()
    # 16
    title = u"世界耐力锦标赛志愿者"
    jobtime = u"8H"
    place = u"上海赛车场"
    salary = u"120"
    day = u"1天"
    demand = u"120包饭"
    job16 = JobController.create_jobinfo(zhen_ag_userindex, title, jobtime, place, salary, day, demand)
    zhen_ag_userindex.JobTxMap[unicode(job16.id)] = ""
    zhen_ag_userindex.save()

    # 17
    title = u"农场嘉年华健康跑"
    jobtime = u"8H"
    place = u"上海市嘉定区博园路4285号"
    salary = u"100"
    day = u"1天"
    demand = u"无"
    job17 = JobController.create_jobinfo(tj_ag_userindex, title, jobtime, place, salary, day, demand)
    tj_ag_userindex.JobTxMap[unicode(job17.id)] = ""
    tj_ag_userindex.save()
    # 18
    title = u"无人机电子音乐嘉年华志愿者"
    jobtime = u"3H"
    place = u"上海汽车博览公园"
    salary = u"80"
    day = u"1天"
    demand = u"无"
    job18 = JobController.create_jobinfo(tj_ag_userindex, title, jobtime, place, salary, day, demand)
    tj_ag_userindex.JobTxMap[unicode(job18.id)] = ""
    tj_ag_userindex.save()
    # 19
    title = u"篮球赛主持人"
    jobtime = u"4H"
    place = u"同济嘉定校区"
    salary = u"200"
    day = u"1天"
    demand = u"女生，有主持经验者"
    job19 = JobController.create_jobinfo(tj_ag_userindex, title, jobtime, place, salary, day, demand)
    tj_ag_userindex.JobTxMap[unicode(job19.id)] = ""
    tj_ag_userindex.save()
    # 20
    title = u"国际小丑节"
    jobtime = u"6H: 30M"
    place = u"同济嘉定校区"
    salary = u"100"
    day = u"2天"
    demand = u"无"
    job20 = JobController.create_jobinfo(tj_ag_userindex, title, jobtime, place, salary, day, demand)
    tj_ag_userindex.JobTxMap[unicode(job20.id)] = ""
    tj_ag_userindex.save()

    return return_data(data={"result": "finish"})


def main():
    pass


if __name__ == '__main__':
    main()
