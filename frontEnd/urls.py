from django.urls import path
from . import views

urlpatterns = [
    path("", views.getLoginPage, name="login"),
    path("main/", views.getMainPage, name="main"),
    path("getCoorList/", views.getCoorList, name="coors")
]
