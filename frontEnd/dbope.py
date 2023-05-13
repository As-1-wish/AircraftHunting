from django.core.exceptions import ObjectDoesNotExist

from frontEnd.models import *
from frontEnd.util import *


# 插入新用户
def insertUser(username, passeword):
    suffix = getRandomStr()
    pwd = Encrypt(passeword + suffix)
    user = User(username=username, password=pwd, pwdsuffix=suffix)
    user.save()


# 根据用户名查找用户
def getUserByName(username):
    try:
        User.objects.get(username=username)
    except ObjectDoesNotExist:
        return False
    else:
        return True


# 检查用户是否合法
def checkUser(username, password):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return -1  # 用户不存在
    else:
        if user.password != Encrypt(password + user.pwdsuffix):
            return 0  # 密码不正确
        else:
            return 1  # 可以登录


# 存储演示记录,并返回此条记录的id
def insertRecord(recordTime, result):
    record = Recording(demoTime=recordTime, demoResult=result)
    record.save()
    return record.id


# 存储轨迹点
def insertTrackPoint(record, airType, tracks, speed):
    tra = []
    for i in range(len(tracks)):
        for j in range(len(tracks[i])):
            tra.append(Track(aircraftType=airType, aircraftID=j, recordId=record, coorX=tracks[i][j][0],
                             coorY=tracks[i][j][1], speed=speed, rank=i))
    print(tra)
    Track.objects.bulk_create(tra)


def recording(recordId):
    return Recording.objects.get(id=recordId)