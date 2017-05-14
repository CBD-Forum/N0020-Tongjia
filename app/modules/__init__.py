#!/usr/bin/env python  
# -*- coding: utf-8 -*-


# !/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum
import uuid
from datetime import datetime

from app.db import mongodb as db
from app.utils.jsonutil import parse_json, to_json
from app.blockchain.userinfo import BlockChainUserInfoMixIn
from app.blockchain.tx import BlockChainTxMixIn
from app.blockchain.jobinfo import BlockChainJobInfoMixIn
from app.utils.util import *

MAP_TO_MONGODB_DOC = False


def to_int(s):
    try:
        return int(s)
    except ValueError:
        return 0


def to_float(s):
    try:
        return float(s)
    except ValueError:
        return 0


class BaseModule(object):
    @classmethod
    def load_from_json(cls, json_str, bcid=None):
        data = parse_json(json_str)
        if data is None:
            return None
        return cls.load_from_dict(data)

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        c = cls()
        bcid = data.get("BCID")
        for a, b in data.iteritems():
            if hasattr(c, a):
                if isinstance(b, dict):
                    cls_for_dict = clss.get(a, None)
                    if cls_for_dict is None:
                        raise TypeError(u"一定要填写dict对应的类 for %s" % a)
                    ins = cls_for_dict.load_from_dict(b, bcid)
                    setattr(c, a, ins)

                elif isinstance(b, (list, tuple)):
                    cls_in_list = clss.get(a, None)
                    if cls_in_list is None:
                        setattr(c, a, [x for x in b])
                    else:
                        l = list()
                        for x in b:
                            if isinstance(x, dict):
                                ins = cls_in_list.load_from_dict(x, bcid)
                            else:
                                raise TypeError(u"list 中如果是类那么对应的一定是dict，且这个类继承于BaseModule for %s: %s" % a, x)
                            l.append(ins)
                        setattr(c, a, l)
                else:
                    setattr(c, a, b)

        return c

    def dump_to_json(self, to_blockchain=False):
        return to_json(self.dump_to_dict(to_blockchain))

    def dump_to_dict(self, to_blockchain=False):
        # return dict(self)
        d = dict()
        for k, v in self:
            if isinstance(v, BaseModule):
                d[k] = v.dump_to_dict(to_blockchain)
            elif isinstance(v, (int, float)) and to_blockchain:
                d[k] = unicode(v)
            else:
                d[k] = v
        return d

    def __iter__(self):
        return self.__dict__.iteritems()


class UserRole(IntEnum):
    Student = 0
    Agency = 1
    Admin = 2

    @classmethod
    def get(cls, num):
        mapping = {0: UserRole.Student,
                   1: UserRole.Agency,
                   2: UserRole.Admin}
        return mapping.get(num, UserRole.Student)

    pass


UserRoleMapping = {0: "学生", 1: "兼职中介", 2: "管理员"}


class UserIndex(db.Document, BaseModule):
    BCID = db.StringField()  # blockchain id

    Username = db.StringField(required=True)
    Password = db.StringField(required=True)

    UserID = db.StringField(default='')
    IDNo = db.StringField(default='')
    RealName = db.StringField(default='')
    Gender = db.IntField(default=0)
    Tele = db.StringField(default='')

    Role = db.IntField(default=0)

    AgencyName = db.StringField(default='')
    School = db.StringField(default='')
    StuID = db.StringField(default='')

    Status = db.IntField(default=1)

    JobTxMap = db.MapField(field=db.StringField(), default={})
    # db.ListField(db.StringField(), default=[])
    CurrentCreditScore = db.IntField(default=6)  # need to update
    TotalCreditScore = db.IntField(default=6)
    RateCount = db.IntField(default=1)

    def __hash__(self):
        return hash(self.UserID)

    def __eq__(self, other):
        return self.UserID

    @classmethod
    def load_from_json(cls, json_str, bcid=None):
        return cls.from_json(json_str)

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        userid = data.get("UserID", None)
        if userid is None:
            u = cls()
            from_local = False
        else:
            u = UserIndex.objects.filter(UserID=userid).first()
            from_local = True
            if u is None:
                u = cls()
                from_local = False
        # u = UserIndex()
        if bcid is not None:
            u.BCID = bcid
        if not from_local:
            u.Username = data.get("Username", "")
            u.Password = data.get("Password", "")

        u.UserID = data.get("UserID", "")
        u.RealName = data.get("RealName", "")
        u.Gender = to_int(data.get("Gender", 0))
        u.Tele = data.get("Tele", "")

        u.Role = to_int(data.get("Role", 0))

        u.AgencyName = data.get("AgencyName", "")
        u.School = data.get("School", "")
        u.StuID = data.get("StuID", "")

        u.Status = to_int(data.get("Status", 1))
        u.save()
        return u

    def dump_to_dict(self, to_blockchain=False):
        d = self.to_mongo()
        d.pop("_id", None)  # _id belong to mongodb
        d.pop("BCID", None)
        d.pop("Jobs", None)
        d.pop("JobTxMap", None)
        if to_blockchain:
            d.pop("CurrentCreditScore", None)
            d.pop("TotalCreditScore", None)
            d.pop("RateCount", None)
            d.pop("IDNo", None)
            for k, v in d.iteritems():
                d[k] = unicode(v)
        else:
            d["Score"] = d["CurrentCreditScore"]
            d.pop("Password", None)
        return d


class JobDetail(db.Document, BaseModule):
    # def __init__(self, jobtime="", place="", salary="", day="", demand=""):
    #     self.JobTime = jobtime
    #     self.Place = place
    #     self.Salary = salary
    #     self.Day = day
    #     self.Demand = demand
    Title = db.StringField(default='')
    JobTime = db.StringField()
    Place = db.StringField()
    Salary = db.StringField()
    Day = db.StringField()
    Demand = db.StringField()

    @classmethod
    def load_from_json(cls, json_str, bcid=None):
        return cls.from_json(json_str)

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        jobdetail = cls()
        jobdetail.Title = data.get("Title", "")
        jobdetail.JobTime = data.get("JobTime", "")
        jobdetail.Place = data.get("Place", "")
        jobdetail.Salary = data.get("Salary", "")
        jobdetail.Day = data.get("Day", "")
        jobdetail.Demand = data.get("Demand", "")
        return jobdetail

    def dump_to_dict(self, to_blockchain=False):
        d = self.to_mongo()
        d.pop("_id", None)  # _id belong to mongodb
        d.pop("BCID", None)
        # if to_blockchain:
        #     # TODO jump title
        #     d.pop("Title", None)
        if to_blockchain:
            for k, v in d.iteritems():
                d[k] = unicode(v)
        return d


class CreditScore(BaseModule):
    def __init__(self, cur_credit=6, total_credit=6, rate_times=1):
        self.CurrentCreditScore = cur_credit
        self.TotalCreditScore = total_credit
        self.Ratetimes = rate_times
        pass

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        ins = cls()
        ins.CurrentCreditScore = to_int(data.get("CurrentCreditScore", 6))
        ins.TotalCreditScore = to_int(data.get("TotalCreditScore", 6))
        ins.Ratetimes = to_int(data.get("Ratetimes", 1))
        return ins

    def dump_to_dict(self, to_blockchain=False):
        d = super(CreditScore, self).dump_to_dict(to_blockchain)
        if not to_blockchain:
            d["RateCount"] = d["Ratetimes"]
        return d

    def __str__(self):
        return "CurrentCreditScore: %s, TotalCreditScore: %s, Ratetimes: %s" % \
               (self.CurrentCreditScore, self.TotalCreditScore, self.Ratetimes)

    pass


class User(BaseModule, BlockChainUserInfoMixIn):
    def __init__(self, userindex=None, creditscore=None, balance=10000, jobs=None):
        if userindex is None:
            userindex = UserIndex()
        self.UserInfo = userindex
        if creditscore is None:
            creditscore = CreditScore()
        self.CreditScore = creditscore
        self.Balance = balance
        if jobs is None:
            jobs = list()
        self.Jobs = jobs

    @classmethod
    def load_from_json(cls, json_str, bcid=None):
        data = parse_json(json_str)
        if data is None:
            return None
        userinfo = UserIndex.load_from_dict(data["UserInfo"], bcid)
        return User(userindex=userinfo,
                    creditscore=data["CreditScore"],
                    balance=data["Balance"],
                    jobs=data["Jobs"])

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        ins = super(User, cls).load_from_dict(data, bcid, UserInfo=UserIndex, CreditScore=CreditScore)
        ins.Balance = to_int(ins.Balance)
        return ins

    # TODO dumptodict balance

    # blockchain related
    def blockchain_create_params(self):
        return [self.UserInfo.UserID, self.dump_to_json(True)]

    def blockchain_delete_params(self):
        return [self.UserInfo.UserID]

    def blockchain_update_params(self):
        return [self.UserInfo.UserID, self.dump_to_json(True)]


class Tx(db.Document, BaseModule, BlockChainTxMixIn):
    JobID = db.StringField()
    UserID = db.StringField()
    ApplyTime = db.StringField()
    # State = db.IntField(default=0)
    Status = db.StringField(default='')
    StuScore = db.IntField(default=0)
    AgencyScore = db.IntField(default=0)

    def blockchain_create_params(self):
        # return [self.TxID, self.dump_to_json()]
        return [unicode(self.id), self.dump_to_json(True)]

    def blockchain_check_params(self, result):
        return [unicode(self.id), unicode(result)]

    def blockchain_evaluate_params(self, userid, score):
        return [unicode(self.id), userid, unicode(score)]

    @classmethod
    def load_from_json(cls, json_str, bcid=None):
        return cls.from_json(json_str)

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        txid = data.get("TxID", None)
        if txid is None:
            tx = cls()
        else:
            tx = Tx.objects.filter(id=txid).first()
            if tx is None:
                tx = cls()

        tx.JobID = data.get("JobID", "")
        tx.UserID = data.get("UserID", "")
        tx.ApplyTime = data.get("ApplyTime", "")
        tx.Status = data.get("Status", '')
        tx.StuScore = to_int(data.get("StuScore", 0))
        tx.AgencyScore = to_int(data.get("AgencyScore", 0))

        tx.save()
        return tx

    def dump_to_dict(self, to_blockchain=False):
        d = self.to_mongo().to_dict()
        if to_blockchain:
            if d["StuScore"] == 0:
                d["StuScore"] = ''
            if d["AgencyScore"] == 0:
                d["AgencyScore"] = ''
        else:
            d["State"] = get_status(d["Status"])
            student = UserIndex.objects.filter(UserID=d.get("UserID", '')).first()
            if student is not None:
                d["UserInfo"] = student.dump_to_dict()
            t = int(d["ApplyTime"])
            d["Time"] = t
            d["ApplyTime"] = datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M')

        if "_id" not in d:
            raise Exception("Tx doesn't has id field!")

        d["TxID"] = unicode(d.pop("_id"))
        if to_blockchain:
            for k, v in d.iteritems():
                d[k] = unicode(v)
        return d


STATUS_MAP = {u"未通过": 0,
              u"已通过": 1,
              u"已评价": 2,
              u"已结算": 3,
              u"中介审核": 4}


def get_status(s):
    if s == '':
        return 0
    for k in STATUS_MAP.iterkeys():
        if s.find(k) != -1:
            return STATUS_MAP[k]
    return 0


class JobInfo(db.Document, BaseModule, BlockChainJobInfoMixIn):
    # def __init__(self, jobid=None, agency="", userid="", jobdetail=None, txs=None,
    #              totalapplied=0, waitcheck=0, hired=0, settled=0):
    #     """
    #
    #     :param jobid:
    #     :type jobid str | None
    #     :param username:
    #      :type username str
    #     :param userid:
    #      :type userid str
    #     :param jobdetail:
    #      :type jobdetail str
    #     :param txs:
    #     :type txs list
    #     :param totalapplied:
    #      :type totalapplied int
    #     :param waitcheck:
    #      :type waitcheck int
    #     :param hired:
    #      :type hired int
    #     :param settled:
    #      :type settled int
    #     """
    #     self.AgencyName = agency
    #     self.UserID = userid
    #     if jobdetail is None:
    #         jobdetail = JobDetail("", "", 0, 0, "")
    #     self.JobDetail = jobdetail
    #     if txs is None:
    #         txs = list()
    #     self.Txs = txs
    #     self.TotalApplied = totalapplied
    #     self.TotalWaitCheck = waitcheck
    #     self.TotalHired = hired
    #     self.TotalSettled = settled
    #     if not jobid:  # jobid is 0, "", None
    #         jobid = str(uuid.uuid4())
    #     self.JobID = jobid

    AgencyName = db.StringField()
    UserID = db.StringField()
    JobDetail = db.ReferenceField(JobDetail)
    Txs = db.ListField(db.ReferenceField(Tx))
    TotalApplied = db.IntField(default=0)
    TotalWaitCheck = db.IntField(default=0)
    TotalHired = db.IntField(default=0)
    TotalSettled = db.IntField(default=0)
    PublishTime = db.IntField(default=0)

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        return super(JobInfo, cls).load_from_dict(data, bcid, JobDetail=JobDetail)

    def blockchain_jobrelated_params(self):
        # return [self.JobID]
        return [unicode(self.id)]

    def blockchain_create_params(self):
        # return [self.JobID, self.dump_to_json()]
        return [unicode(self.id), self.dump_to_json(True)]

    def blockchain_update_params(self):
        # return [self.JobID, self.dump_to_json()]
        return [unicode(self.id), self.dump_to_json(True)]

    def blockchain_delete_params(self):
        # return [self.JobID]
        return [unicode(self.id)]

    def blockchain_addtx_params(self, txid):
        # return [self.JobID, txid]
        return [unicode(self.id), unicode(txid)]

    @classmethod
    def load_from_json(cls, json_str, bcid=None):
        return cls.from_json(json_str)

    @classmethod
    def load_from_dict(cls, data, bcid=None, **clss):
        jobid = data.get("JobID", None)
        if jobid is None:
            jobinfo = cls()
            from_source = False
        else:
            jobinfo = JobInfo.objects.filter(id=jobid).first()
            from_source = True
            if jobinfo is None:
                jobinfo = cls()
                from_source = True
        if from_source:
            jobdetail_data = data.get("JobDetail", {})
            jobinfo.JobDetail.JobTime = jobdetail_data.get("JobTime", "")
            jobinfo.JobDetail.Place = jobdetail_data.get("Place", "")
            jobinfo.JobDetail.Salary = jobdetail_data.get("Salary", "")
            jobinfo.JobDetail.Day = jobdetail_data.get("Day", "")
            jobinfo.JobDetail.Demand = jobdetail_data.get("Demand", "")
            jobinfo.JobDetail.save()
        else:
            jobdetail = JobDetail.load_from_dict(data.get("JobDetail", {}))  # data.get("AgencyName", "")
            jobdetail.save()
            jobinfo.JobDetail = jobdetail

        jobinfo.Txs = []
        for t in data.get("Txs", []):
            if len(t) == 24:
                print t
                tx = Tx.objects.filter(id=t).first()
                if tx is not None:
                    jobinfo.Txs.append(tx)

        jobinfo.AgencyName = data.get("AgencyName", "")
        jobinfo.UserID = data.get("UserID", "")

        jobinfo.TotalApplied = to_int(data.get("TotalApplied", 0))
        jobinfo.TotalWaitCheck = to_int(data.get("TotalWaitCheck", 0))
        jobinfo.TotalHired = to_int(data.get("TotalHired", 0))
        jobinfo.TotalSettled = to_int(data.get("TotalSettled", 0))

        jobinfo.save()

        return jobinfo

    def dump_to_dict(self, to_blockchain=False):
        d = self.to_mongo().to_dict()
        print d
        if "_id" not in d:
            raise Exception("JobInfo doesn't has id field!")
        d["JobID"] = unicode(d.pop("_id"))
        d.pop("CreditScore", None)
        d.pop("BCID", None)
        if to_blockchain:
            d["Txs"] = [unicode(i.id) for i in self.Txs]
            d.pop("PublishTime", None)
        else:
            d["Txs"] = [i.dump_to_dict(to_blockchain) for i in self.Txs]
            d["Time"] = d["PublishTime"]
            d["PublishTime"] = datetime.fromtimestamp(d["PublishTime"]).strftime('%Y-%m-%d %H:%M')
        d["JobDetail"] = self.JobDetail.dump_to_dict(to_blockchain)
        if to_blockchain:
            d["TotalApplied"] = unicode(d["TotalApplied"])
            d["TotalWaitCheck"] = unicode(d["TotalWaitCheck"])
            d["TotalHired"] = unicode(d["TotalHired"])
            d["TotalSettled"] = unicode(d["TotalSettled"])
        return d


def main():
    pass


if __name__ == '__main__':
    main()
