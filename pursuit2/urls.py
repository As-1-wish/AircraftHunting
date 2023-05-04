from django.urls import path
from pursuit2.views import Evaluate

app_name = "pursuit2"

urlpatterns = [
    path('evaluate', Evaluate, name='evaluate'),
]
