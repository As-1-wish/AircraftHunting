from django.urls import path
from . import views

urlpatterns = [
    path("", views.getLoginPage, name="loginPage"),
    path("main/", views.getMainPage, name="main"),
    path("login/", views.login),
    path("register/", views.getRegister, name="register"),
    path("init/", views.initCoordinate, name='init'),
    path("insertDemo/", views.insertDemo, name='insertDemo'),
    path("getAllDemos/", views.getAllDemos, name='getAllDemos')
]
