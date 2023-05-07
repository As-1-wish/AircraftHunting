from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from frontEnd import dbope


# Create your views here.


def getLoginPage(request):
    return render(request, "login.html")


def getMainPage(request):
    return render(request, "main.html")


# 新增用户
def register(request, username, password):
    if dbope.getUserByName(username):
        dbope.insertUser(username, password)
        return JsonResponse({'code': 0, 'msg': '插入成功'})
    else:
        return JsonResponse({'code': 1, 'msg': '用户名已存在'})


# 检查请求登录用户合法性
def login(request):
    if request.is_ajax():
        username = request.GET.get('username')
        password = request.GET.get('password')
        tag = dbope.checkUser(username, password)
        if tag == 1:
            return JsonResponse({'code': 0, 'msg': '登录成功！'})
        elif tag == 0:
            return JsonResponse({'code': 1, 'msg': '密码错误！'})
        else:
            return JsonResponse({'code': 1, 'msg': '用户不存在！'})
    else:
        return JsonResponse({'code': 1, 'msg': '请求失败！'})
