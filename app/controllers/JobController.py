#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from app.modules import JobInfo, JobDetail
from .UserController import get_all_agnecy, get_userindex_byuserid
from app.utils import util


# def get_jobindex(**argv):
#     return JobInfoIndex.objects.filter(**argv).first()  # return None


# def get_job_bcid(jobid):
#     return get_jobindex(JobID=jobid)


# def get_tx_txid(bcid):
#     return get_jobindex(BCID=bcid)

def get_job(**argv):
    return JobInfo.objects.filter(**argv).first()  # return None


def get_job_by_jobid(jobid):
    # return get_job(JobID=jobid)
    return get_job(id=jobid)


def get_job_list(**argv):
    return JobInfo.objects.filter(**argv).all()  # return None


def get_job_list_by_order(*argv):
    return JobInfo.objects.order_by(*argv)


def get_jobs_by_agency_userid(userid):
    return get_job_list(UserID=userid)


def get_all_agency_and_jobs():
    agnecy_list = get_all_agnecy()
    l = set(agnecy_list)
    l = sorted(l, key=lambda x: x.CurrentCreditScore, reverse=True)
    ret = list()
    # for a in agnecy_list:
    for a in l:
        # print a.UserID, a.Username
        jobs = get_job_list(UserID=a.UserID)
        agency_name = unicode(a.AgencyName)
        score = float(a.CurrentCreditScore)
        job_list = list()
        for j in jobs:
            job_list.append(j.dump_to_dict())
        ret.append((agency_name, score, job_list))
    return ret


def get_all_jobs_by_time(max_count=20):
    return get_job_list_by_order("-PublishTime")


def create_jobdetail(title, jobtime, place, salary, day, demand):
    jobdetail = JobDetail(Title=title,
                          JobTime=jobtime,
                          Place=place,
                          Salary=unicode(salary),
                          Day=unicode(day),
                          Demand=demand)
    jobdetail.save()
    return jobdetail


def create_jobinfo(userindex, title, jobtime, place, salary, day, demand):
    jobdetail = create_jobdetail(title, jobtime, place, salary, day, demand)
    job = JobInfo(AgencyName=userindex.AgencyName,
                  UserID=userindex.UserID,
                  JobDetail=jobdetail)
    job.PublishTime = util.get_time()
    job.save()
    job.bc_create()

    print job

    # to blockchain
    # job.bc_create()

    # cache
    # jobindex = JobInfoIndex(JobID=job.JobID,
    #                         TotalApplied=job.TotalApplied,
    #                         JobDetail=jobdetail)
    # jobindex.save()
    #
    # agencyindex = get_agencyindex_byid(user.UserInfo.UserID)
    # if agencyindex is None:
    #     agencyindex = AgencyIndex(UserID=user.UserInfo.UserID,
    #                               AgencyName=user.UserInfo.AgencyName,
    #                               CreditScore=user.CreditScore.CurrentCreditScore)
    # agencyindex.JobIndexList.append(jobindex)
    # agencyindex.save()
    return job


def main():
    pass


if __name__ == '__main__':
    main()
