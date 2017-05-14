#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from flask import request, flash, redirect, url_for, session
from . import app
from .routersutil import *

from app.controllers import UserController, JobController
from app.modules import UserIndex, User, UserRole, UserRoleMapping
from app.utils import hashutil


# user
@app.route('/user/login', methods=['GET', 'POST'])
@allow_cross_domain
def login():
    form = UserController.LoginForm(request.form)
    msg = ''
    role = UserRole.Student
    if request.method == 'POST':
        ajax = False
        if request_wants_json():
            ajax = True
            data = get_data_from_ajax()
            form.username.data = unicode(data.get('username', None))
            form.password.data = unicode(data.get('password', None))
            role = data.get('role', None)
            role = int(role) if role is not None else UserRole.Student
        if ajax or form.validate_on_submit():
            username = form.username.data
            password = hashutil.hash_md5(form.password.data)
            userindex = UserController.get_userindex_byname(username)
            role = UserRole.get(role)
            if userindex is None:
                # userindex = UserController.create_userindex(username, password, role)
                # token = UserController.generate_token(username)
                # return return_data(None, {'token': token, 'detail': False},
                #                    msg="register success for %s" % userindex.Username)
                abort(403, "该用户不存在，请先注册！")
            else:
                if password == userindex.Password:
                    if role != userindex.Role:
                        abort(403, u"该用户登陆时选择了不同的身份(应该为：%s)" % UserRoleMapping.get(userindex.Role, u"学生"))

                    # enter index page
                    # session['user'] = userindex.username
                    msg = 'You were successfully login in for user:%s !' % username
                    flash(msg)
                    # if request_wants_json():
                    #     return jsonify(jsonutil.json_wrapper({}, 0, msg))
                    token = UserController.generate_token(username)

                    detail = False if userindex.UserID == '' else True
                    return return_data(None, {'token': token, 'detail': detail},
                                       msg="login success for %s" % userindex.Username)
                else:
                    msg = u"密码错误！"
                    flash(msg)
            pass
        else:
            msg = u'用户名或者密码不符合要求(最小3位最长20位)'
            flash(msg)
    else:
        msg = u'请登陆'
        flash(msg)

    if request_wants_json():
        abort(401, msg)

    return render_template('login.html', form=form, info=msg)


@app.route('/user/register', methods=['GET', 'POST'])
@allow_cross_domain
def register():
    data = get_data_from_ajax()
    username = data.get('username', None)
    password = data.get('password', None)
    role = data.get('role', None)
    if username is None or password is None or role is None:
        abort(400, u"必须填写username和password和role")

    username = unicode(username)
    userindex = UserController.get_userindex_byname(username)
    if userindex is not None:
        abort(403, u"该用户(%s)已经注册过" % username)

    password = hashutil.hash_md5(unicode(password))
    try:
        role = int(role) if role is not None else UserRole.Student
    except ValueError, e:
        abort(403, u"Role 必须为整数")

    if role not in [0, 1]:
        abort(403, u"Role 必须为 0 或 1")

    userindex = UserController.create_userindex(username, password, role)
    token = UserController.generate_token(username)
    return return_data(None, {'token': token, 'detail': False},
                       msg="register success for %s" % userindex.Username)


@app.route('/user/detail', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth
def finish_userdetail_info(userindex):
    data = get_data_from_ajax()
    userid = data.get("UserID", None)
    if userid is None:
        userid = data.get("IDNo", None)
    realname = data.get("RealName", None)
    gender = data.get("Gender", None)
    tele = data.get("Tele", None)

    userindex.IDNo = userid
    userindex.RealName = realname
    userindex.Gender = gender
    userindex.Tele = tele
    check_list = list()
    check_list.append(userid)
    check_list.append(realname)
    if userindex.Role == UserRole.Student:
        school = data.get("School")
        stuid = data.get("StuID")
        userindex.School = school
        userindex.StuID = stuid
        check_list.append(school)
        check_list.append(stuid)

        if check_list.count(None):
            abort(400, u"缺少完整参数: %d" % check_list.index(None))
        userindex.School = school
        userindex.StuID = stuid
    elif userindex.Role == UserRole.Agency:
        agencyname = data.get("AgencyName")
        check_list.append(agencyname)
        if check_list.count(None):
            abort(400, u"缺少完整参数: %d" % check_list.index(None))
        userindex.AgencyName = agencyname
    else:
        abort(400, "role error!")

    user = UserController.create_user(userindex)
    return return_data(None, data=user.dump_to_dict())


# @app.route('/user/modify', methods=['GET', 'POST'])
# @allow_cross_domain
# @check_auth
# def modify_userinfo(userindex):
#     data = get_data_from_ajax()
#     for k, v in data.iteritems():
#         if hasattr(userindex, k):
#             setattr(userindex, k, v)
#
#     UserController.update_userinfo(userindex)
#     return return_data(None, data=userindex.dump_to_dict())


@app.route('/user/info', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def userinfo(userindex):
    # data = get_data_from_ajax()
    # if data is None:
    #     return
    u = User.from_blockchain(userindex.UserID)
    if u is None:
        abort(403, u"用户不存在于区块链记录中或访问区块链失败")
    u.UserInfo.CurrentCreditScore = u.CreditScore.CurrentCreditScore
    u.UserInfo.TotalCreditScore = u.CreditScore.TotalCreditScore
    u.UserInfo.RateCount = u.CreditScore.Ratetimes
    u.UserInfo.save()
    d = UserController.wrapper_userinfo(u)

    # return return_data(None, data=u.dump_to_dict())
    return return_data(None, data=d)


@app.route('/user/score', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def userinfo_score(userindex):
    return return_data(None, data={
        "CurrentCreditScore": userindex.CurrentCreditScore,
        "TotalCreditScore": userindex.TotalCreditScore,
        "RateCount": userindex.RateCount,
    })


@app.route('/user/allagency', methods=['GET', 'POST'])
@allow_cross_domain
def get_all_agency():
    data = UserController.get_all_agnecy(True)
    print data
    return return_data(None, data=data)


@app.route('/user/agency', methods=['GET', 'POST'])
@allow_cross_domain
def user_agency():
    data = get_data_from_ajax()
    jobid = data.get("JobID", None)
    if jobid is None:
        abort(400, "缺少 JobID")

    jobinfo = JobController.get_job_by_jobid(jobid)
    if jobinfo is None:
        abort(403, "查询的 JobID: %s 不存在" % jobid)

    userindex = UserController.get_userindex_byuserid(jobinfo.UserID)
    d = userindex.dump_to_dict()
    d["Score"] = userindex.CurrentCreditScore
    d["JobsCount"] = len(userindex.JobTxMap)
    return return_data(None, data=d)


@app.route('/user/update/balance', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def update_balance(userindex):
    data = get_data_from_ajax()
    balance = data.get("Balance", None)
    if balance is None:
        abort(400, u"缺少参数Balance")

    user = UserController.update_user_balance(userindex.UserID, balance)
    return return_data(None, data=user.dump_to_dict())


@app.route('/user/update/score', methods=['GET', 'POST'])
@allow_cross_domain
@check_auth_ext
def update_score(userindex):
    data = get_data_from_ajax()
    score = data.get("Score", None)
    if score is None:
        abort(400, u"缺少参数Score")

    try:
        score = int(score)
    except ValueError:
        score = -1

    if not (0 <= score <= 10):
        abort(403, u"Score 必须在 0<score<=10 之间")

    user = UserController.update_user_current_score(userindex.UserID, score)
    return return_data(None, data=user.dump_to_dict())
