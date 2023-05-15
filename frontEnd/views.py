import json
import random
from datetime import datetime

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pymysql import IntegrityError

from frontEnd import dbope
from frontEnd.constant import *


# Create your views here.


def getLoginPage(request):
    return render(request, "login.html")


def getMainPage(request):
    return render(request, "main.html")


def getRegister(request):
    return render(request, "register.html")


# 新增用户
def register(request, username, password):
    if dbope.getUserByName(username):
        dbope.insertUser(username, password)
        return JsonResponse({'code': 0, 'msg': '插入成功'})
    else:
        return JsonResponse({'code': 1, 'msg': '用户名已存在'})


# 检查请求登录用户合法性
@csrf_exempt
def login(request):
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        tag = dbope.checkUser(username, password)
        if tag == 1:
            return JsonResponse({'code': 0, 'msg': '登录成功！'})
        elif tag == 0:
            return JsonResponse({'code': 1, 'msg': '密码错误！'})
        else:
            return JsonResponse({'code': 1, 'msg': '用户不存在！'})
    else:
        return JsonResponse({'code': 1, 'msg': '请求失败！'})


# 根据前台数据生成对应数量的无人机初始位置
@csrf_exempt
def initCoordinate(request):
    if request.is_ajax() and request.method == 'POST':
        enemyNum = int(request.POST.get('enemyNum'))
        friendNum = int(request.POST.get('friendNum'))
        enemys, friends, airs = [], [], []
        cnt = 0
        # 随机生成敌机初始位置
        while cnt < enemyNum:
            x = random.randint(COOR_MIN, COOR_MAX)
            y = random.randint(COOR_MIN, COOR_MAX)
            if checkOcclusion(airs, [x, y]):
                cnt += 1
                enemys.append([x, y])
                airs.append([x, y])
        cnt = 0
        # 随机生成友机初始位置
        while cnt < friendNum:
            x = random.randint(COOR_MIN, COOR_MAX)
            y = random.randint(COOR_MIN, COOR_MAX)
            if checkOcclusion(airs, [x, y]):
                cnt += 1
                friends.append([x, y])
                airs.append([x, y])

        return JsonResponse({'enemy': enemys, 'friend': friends, 'code': 0})
    else:
        return JsonResponse({'code': 1})


# 判断坐标是否遮挡
def checkOcclusion(airs, pre):
    for i in airs:
        if abs(i[0] - pre[0]) < aircraft_size / rank_x or abs(i[1] - pre[1]) < aircraft_size / rank_y:
            return False
    return True


# 插入本次演示记录
@csrf_exempt
def insertDemo(request):
    if request.is_ajax() and request.method == 'POST':
        result = request.POST.get('result')
        enemy = json.loads(request.POST.get('enemy'))
        friend = json.loads(request.POST.get('friend'))
        speed = request.POST.get('speed')
        preTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            demo_id = dbope.insertRecord(preTime, result)
            demo = dbope.getDemoByID(demo_id)

            dbope.insertTrackPoint(demo, 1, friend, speed)
            dbope.insertTrackPoint(demo, 2, enemy, speed)
            return JsonResponse({'code': 0, 'msg': "插入成功"})
        except IntegrityError as e:
            return JsonResponse({'code': 1, 'msg': str(e)})


# 获得演示记录列表
def getAllDemos(request):
    if request.is_ajax() and request.method == 'GET':
        records = dbope.getAllDemos()
        print(records[0][1])
        return JsonResponse({'code': 0, 'records': dbope.getAllDemos()})
