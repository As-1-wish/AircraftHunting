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


def checkUser(username, password):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return -1     # 用户不存在
    else:
        print(user.password, Encrypt(password + user.pwdsuffix))
        if user.password != Encrypt(password + user.pwdsuffix):
            return 0  # 密码不正确
        else:
            return 1  # 可以登录
