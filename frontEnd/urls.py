from django.urls import path
from . import views

urlpatterns = [
    path("", views.getLoginPage, name="loginPage"),
    path("main/", views.getMainPage, name="main"),
    path("getCoorList/", views.getCoorList, name="coors"),
    path("login/", views.login),
    path("register/", views.register, name="register")
]
