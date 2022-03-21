import json
from datetime import datetime

import django_otp
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from .forms import UserLoginForm
from .models import Uporabnik


@login_required(login_url='/login')
def landing_page(request):
    context_example = "TEST"
    return render(request, 'landing_page.html', context={"exmp1": context_example})


def login(request):
    if request.method == "GET":
        return render(request, "login_page.html", context={"form": UserLoginForm})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect("/")
        else:
            return render(request, "login_page.html", context={"form": UserLoginForm, "error": "Uporabniško ime in/ali geslo je napačno."})




@login_required
def createOTP(request):
    try:
        device = TOTPDevice.objects.get(user=request.user)
        device.confirmed = True
        device.save()

        if django_otp.match_token(request.user, "code_here"):
            return HttpResponse(content=json.dumps({"status": True}),
                                content_type="application/json",
                                status=status.HTTP_201_CREATED)
        else:
            device.confirmed = False
            device.save()
            return HttpResponse(content=json.dumps({"status": False}),
                                content_type="application/json",
                                status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return HttpResponse(content=json.dumps({"status": True}),
                            content_type="application/json",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def disableOTP(request):
    try:
        totp_devices = TOTPDevice.objects.filter(user=request.user)
        if totp_devices.exists():
            totp_devices.delete()
        return HttpResponse(content=json.dumps({"status": True}),
                            content_type="application/json",
                            status=status.HTTP_200_OK)
    except Exception as e:
        return HttpResponse(content=json.dumps({"status": False}),
                            content_type="application/json",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
