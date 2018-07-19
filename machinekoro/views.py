from django.shortcuts import render,redirect

import time

# Create your views here.


# place holder views

def cover_view(request):
    return render(request, 'static.html')


def main_view(request,serial):
    socker_url = "ws://127.0.0.1:8000/ws/consumers/" + str(serial)
    context = {
        "socket_url":socker_url
    }
    return render(request, 'reactEnabled.html',context)
