from django.http import JsonResponse
from django.shortcuts import render
from frontEnd import coordinates


# Create your views here.


def getLoginPage(request):
    return render(request, "login.html")


def getMainPage(request):
    return render(request, "main.html")


def getCoorList(resquest):
    if resquest.is_ajax():
        return JsonResponse({'friendly_list': coordinates.friendly_coordinate_list,
                             'enemy_list': coordinates.enemy_coordinate_list})
