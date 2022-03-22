import json
from datetime import datetime

import django_otp
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from .forms import UserLoginForm, CreateNewProjectForm, OTPForm, NewZgodbaForm
from .models import Uporabnik, Projekt, Zgodba, Clan



@login_required
def landing_page(request):
    projekti = Projekt.objects.all()
    uporabniki = Uporabnik.objects.all()
    return render(request, 'landing_page.html', context={"projekti": projekti, "uporabniki": uporabniki, "forms": {
        "projekt_form": CreateNewProjectForm()
    }})


@login_required(login_url='/login')
def create_new_project(request):
    new_project = request.POST["ime"]
    project = Projekt.objects.create(ime=new_project)
    project.save()

    Clan.objects.create(projekt=project, uporabnik=request.user, vloga=0).save()
    return redirect("/")


@login_required(login_url='/login')
def delete_project(request, id):
    Projekt.objects.filter(id=id).delete()
    return redirect("/")


def login_page(request):
    if request.method == "GET":
        return render(request, "login_page.html", context={"form": UserLoginForm})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print("User: ", user)
        if user is not None:
            login(request, user)
            if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
                user.otp_auth = False
                user.save()
                return redirect("loginOTP")
            else:
                return redirect("landing_page")
        else:
            return render(request, "login_page.html", context={"form": UserLoginForm, "error": "Uporabniško ime in/ali geslo je napačno."})


@login_required
def createOTP(request):
    try:
        device = TOTPDevice.objects.get(user=request.user)
        device.confirmed = True
        device.save()

        if django_otp.match_token(request.user, str(json.loads(request.body.decode('utf-8'))['code'])):
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

@login_required
def loginOTP(request):
    if request.method == "POST":
        form = OTPForm(data=request.POST)
        if form.is_valid():
            if django_otp.match_token(request.user, form.cleaned_data.get('otp_code')):
                user = request.user
                user.otp_auth = True
                user.save()
                return redirect("landing_page")
            else:
                return redirect("loginOTP")
    form = OTPForm()
    return render(request=request, template_name="otp_login.html", context={"form": form})


@login_required
def project_page(request, project_id):
    project = get_object_or_404(Projekt, pk=project_id)
    stories = Zgodba.objects.select_related().filter(projekt=project)
    clan = Clan.objects.select_related().get(uporabnik=request.user)

    context = {
        'projekt' : project,
        'zgodbe' : stories,
        'clan' : clan,
        'forms' : {
            'zgodba_form' : NewZgodbaForm()
        }
    }

    return render(request=request, template_name="project_page.html", context=context)


@login_required
def new_story(request, project_id):
    project = get_object_or_404(Projekt, pk=project_id)

    if request.method == 'POST':
        story_form = NewZgodbaForm(request.POST)
        if story_form.is_valid():
            story_instance = story_form.save(commit=False)
            story_instance.projekt = project
            story_instance.save()
            print(story_instance)
            return redirect(f'/projects/{project_id}')
    else:
        story_form = NewZgodbaForm()

    context = {
        'form': story_form,
        'projekt': project,
    }
    return render(request, 'zgodba_form.html', context)
