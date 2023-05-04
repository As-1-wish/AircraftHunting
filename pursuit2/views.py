import requests
from django.http import JsonResponse

from pursuit2.eval import evaluate


# Create your views here.


def Evaluate(request):
    if request.is_ajax():
        enemy = request.GET.get('enemy')
        friend = request.GET.get('friend')
        coors = evaluate(enemy, friend)
        return JsonResponse({'friend': coors[1], 'enemy': coors[0], 'result': coors[2]})
