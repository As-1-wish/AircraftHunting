import os
from django.db import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AircraftHunting.settings")


# Create your models here.
# 用户表
class User(models.Model):
    username = models.CharField(max_length=50)  # 用户名，唯一
    password = models.CharField(max_length=50)  # 密码，经 md5加密
    pwdsuffix = models.CharField(max_length=10)  # 密码后缀

    def __str__(self):
        return self.username


# 模拟记录表
class Recording(models.Model):
    demoTime = models.DateTimeField()  # 演示时间
    demoResult = models.IntegerField()  # 演习结果:0-成功捕获 1-超出捕获距离 -1-围猎失败

    def __str__(self):
        return str(self.demoTime)


# 飞行器运动记录表
class Track(models.Model):

    aircraftType = models.IntegerField()  # 飞行器类别:1-友 2-敌
    aircraftID = models.IntegerField(default=1)  # 飞行器ID，用来区分同次演示中的不同飞行器
    recordId = models.ForeignKey(Recording, on_delete=models.CASCADE)  # 该飞行器对应记录id
    coorX = models.DecimalField(max_digits=10, decimal_places=3)  # x坐标
    coorY = models.DecimalField(max_digits=10, decimal_places=3)  # y坐标
    speed = models.DecimalField(max_digits=10, decimal_places=3)  # 速度
    rank = models.IntegerField()  # 轨迹信息次序

    def __str__(self):
        return "(" + str(self.coorX) + "," + str(self.coorY) + ")-" + str(self.speed)
