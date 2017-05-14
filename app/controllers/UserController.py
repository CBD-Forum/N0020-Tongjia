#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import uuid
from flask import abort
from flask_wtf import Form
from wtforms import StringField, PasswordField, validators
from wtforms.validators import DataRequired

from app.db import redisdb
from app.modules import UserIndex, User, UserRole, JobInfo, Tx
from app.utils import util, hashutil


class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), validators.Length(min=3, max=20)])
    password = PasswordField('password', validators=[DataRequired(), validators.Length(min=3, max=20)])
    # role = RadioField('username', validators=[DataRequired(), validators.Length(min=3, max=20)])
    pass


# token related
class RedisToken(redisdb.RedisMixIn):
    def __init__(self, username=None):
        self.username = username

    def stored_data(self):
        return {"username": self.username}

    pass


# TODO change to expire
# EXPIRE_TIME = 0
EXPIRE_TIME = 60 * 30


def generate_token(username):
    seed = username + unicode(util.get_time(True))
    token = hashutil.hash_md5(seed)
    r_token = RedisToken(username)

    r_token.save_to_redis(token, expire=EXPIRE_TIME)
    return token


def get_username_bytoken(token):
    return RedisToken.load_from_redis(token, EXPIRE_TIME)


# query
def get_userindex(**argv):
    return UserIndex.objects.filter(**argv).first()  # return None


def get_userindex_all(**argv):
    return UserIndex.objects.filter(**argv).all()  # return None


def get_userindex_byname(username):
    return get_userindex(Username=username)


def get_userindex_byuserid(userid):
    return get_userindex(UserID=userid)


def get_userindex_bytoken(token):
    data = get_username_bytoken(token)
    if data is not None:
        return get_userindex_byname(data["username"])
    return None


def get_all_agnecy(to_dict=False):
    l = get_userindex_all(Role=UserRole.Agency)
    if to_dict:
        l = [i.dump_to_dict() for i in l]
    return l


def wrapper_userinfo(u):
    d = u.dump_to_dict()
    ids = d["Jobs"]
    l = list()
    if u.UserInfo.Role == UserRole.Student:
        for i in ids:
            tx = Tx.objects.filter(id=i).first()
            if tx is not None:
                l.append(tx.dump_to_dict())
    elif u.UserInfo.Role == UserRole.Agency:
        for i in ids:
            job = JobInfo.objects.filter(id=i).first()
            if job is not None:
                l.append(job.dump_to_dict())
    d["Jobs"] = l
    d["UserInfo"]["UserID"] = d["UserInfo"]["IDNo"]
    return d


# create
def create_userindex(username, password, role):
    u = UserIndex(Username=username, Password=password, Role=role)
    u.save()
    return u


def update_userindex(userindex, UserID, RealName, Gender, Tele, Role, AgencyName, School, StuID):
    userindex.UserID = UserID
    userindex.RealName = RealName
    userindex.Gender = Gender
    userindex.Tele = Tele
    userindex.Role = Role
    userindex.AgencyName = AgencyName
    userindex.School = School
    userindex.StuID = StuID

    userindex.save()
    return userindex


def update_userindex_role(userindex, role):
    userindex.Role = role
    userindex.save()


def create_user(userindex):
    user = User(userindex)

    userindex.UserID = unicode(uuid.uuid4())
    userindex.save()

    # create to blockchain
    user.bc_create()
    return user


def update_user_balance(userid, balance):
    user = User.from_blockchain(userid)
    if user is None:
        abort(403, "提供的用户未在记录当中")
    user.Balance = balance
    user.bc_update()
    return user


def update_user_current_score(userid, score):
    user = User.from_blockchain(userid)
    if user is None:
        abort(403, "提供的用户未在记录当中")
    user.CreditScore.CurrentCreditScore = score
    user.bc_update()
    user.UserInfo.CurrentCreditScore = score
    user.UserInfo.save()
    return user


def main():
    pass


if __name__ == '__main__':
    main()
