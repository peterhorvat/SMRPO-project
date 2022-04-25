import json
from datetime import datetime
import pytz

import django_otp
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from .decorators import restrict_SM
from .forms import UserLoginForm, CreateNewProjectForm, OTPForm, ZgodbaForm, UporabnikChangeForm, SprintForm, \
    EditSprintForm, EditSprintFormAdmin, NalogaForm, ZgodbaOpombeForm, ObjavaForm
from .models import Uporabnik, Projekt, Zgodba, Clan, ProjectOwner, ScrumMaster, Sprint, Naloga, Objava


@login_required
def landing_page(request):
    if request.user.is_superuser:
        projekti = Projekt.objects.all()
    else:
        user = Uporabnik.objects.get(pk=request.user.id)
        projekti = [i.projekt for i in Clan.objects.filter(uporabnik=user).iterator()] \
                   + [i.projekt for i in ScrumMaster.objects.filter(uporabnik=user).iterator()] \
                   + [i.projekt for i in ProjectOwner.objects.filter(uporabnik=user).iterator()]

    uporabniki = Uporabnik.objects.all()
    return render(request, 'landing_page.html', context={"projekti": projekti, "uporabniki": uporabniki, "forms": {
        "projekt_form": CreateNewProjectForm()
    }, "user_types": ["Product Owner", "Scrum Master", "Team Member "]})


@login_required
def create_new_project(request):
    if str(request.POST["ime"]).strip() == "":
        return JsonResponse({"data": "Ime ne sme biti prazno.", "status": 400})
    elif Projekt.objects.filter(ime=request.POST["ime"]).count() > 0:
        return JsonResponse({"data": "Projekt s tem imenom ze obstaja.", "status": 400})
    project = Projekt.objects.create(ime=request.POST["ime"], opis=request.POST["opis"])
    project.save()
    return JsonResponse({"data": "Ok", "status": 200, "project_id": project.id})


@login_required
def delete_project(request, id):
    Projekt.objects.filter(id=id).delete()
    return redirect("/")


def create_new_clan(request, project_id):
    project = Projekt.objects.get(pk=project_id)
    clani = json.loads(request.POST["selected"])
    for clan in clani:
        print(clan)
        for role in clan['roles']:
            if role == "0":
                new_owner = ProjectOwner(projekt=project, uporabnik=Uporabnik.objects.get(pk=int(clan["id"])))
                new_owner.save()
                continue
            elif role == "1":
                new_maser = ScrumMaster(projekt=project, uporabnik=Uporabnik.objects.get(pk=int(clan["id"])))
                new_maser.save()
            elif role == "2":
                new_clan = Clan(projekt=project, uporabnik=Uporabnik.objects.get(pk=int(clan['id'])))
                new_clan.save()
    return redirect("/")


def login_page(request):
    if request.method == "GET":
        return render(request, "login_page.html", context={"form": UserLoginForm})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
                user.otp_auth = False
                user.save()
                return redirect("loginOTP")
            else:
                return redirect("landing_page")
        else:
            return render(request, "login_page.html",
                          context={"form": UserLoginForm, "error": "Uporabniško ime in/ali geslo je napačno."})


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
def sprint_backlog(request, project_id):
    project = get_object_or_404(Projekt, pk=project_id)
    stories = Zgodba.objects.filter(projekt=project)
    for story in stories:
        if story.sprint is None:
            story.canAddTask = False
        else:
            if story.sprint.zacetni_cas < timezone.now() < story.sprint.koncni_cas:
                story.canAddTask=True
            else:
                story.canAddTask=False
    try:
        clan = Clan.objects.get(uporabnik=request.user, projekt=project)
    except ObjectDoesNotExist:
        clan = None
    try:
        scrum_master = ScrumMaster.objects.get(uporabnik=request.user, projekt=project)
    except ObjectDoesNotExist:
        scrum_master = None
    try:
        product_owner = ProjectOwner.objects.get(uporabnik=request.user, projekt=project)
    except ObjectDoesNotExist:
        product_owner = None
    if clan is None and product_owner is None and scrum_master is None:
        redirect('/404')
    context = {
        'projekt': project,
        'zgodbe': stories,
        'clan': clan,
        'scrum_master': scrum_master,
        'product_owner': product_owner,
        'form': ZgodbaForm()
    }

    return render(request=request, template_name="sprint_backlog.html", context=context)


@login_required
def edit_project(request, project_id):
    projekt = Projekt.objects.get(pk=project_id)
    if request.method == "GET":
        return render(request, "edit_project_page.html",
                      {"projekt_ime": projekt.ime, "projekt_opis": projekt.opis, "form": CreateNewProjectForm()})
    else:
        if request.POST["ime"] != projekt.ime:
            if len(Projekt.objects.filter(ime=request.POST["ime"])) == 0:
                projekt.ime = request.POST["ime"]
            else:
                return JsonResponse({"data": "Ta ime že obstaja !", "status": 400})
        projekt.opis = request.POST["opis"]
        projekt.save()
        return redirect("/")


@login_required
def update_story(request, project_id, story_id):
    temp = Zgodba.objects.filter(ime=request.POST["ime"])
    if len(temp) > 0 and temp[0].id != story_id:
        return JsonResponse("To ime že obstaja!", status=400)
    Zgodba.objects.filter(id=story_id).update(ime=request.POST["ime"], vsebina=request.POST["vsebina"],
                                              sprejemni_testi=request.POST["sprejemni_testi"],
                                              poslovna_vrednost=request.POST["poslovna_vrednost"],
                                              prioriteta=request.POST["prioriteta"]
                                              )
    return redirect("/projects/" + str(project_id))


@login_required
def update_user(request):
    # dictionary for initial data with
    # field names as keys
    context = {}
    current_user = request.user

    if request.method == 'POST':
        # pass the object as instance in form
        form = UporabnikChangeForm(data=request.POST, instance=current_user)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            return redirect('/')

        # add form dictionary to context
        context["form"] = form
    else:
        context['form'] = UporabnikChangeForm(instance=current_user)

    return render(request, "uporabnik_form.html", context)


@login_required
def product_backlog(request, project_id):
    project = get_object_or_404(Projekt, pk=project_id)
    context = {
        'projekt': project,
        'story_form': ZgodbaForm,
        'opombe_form': ZgodbaOpombeForm
    }
    try:
        clan = Clan.objects.get(uporabnik=request.user, projekt=project)
    except ObjectDoesNotExist:
        clan = None
    try:
        scrum_master = ScrumMaster.objects.get(uporabnik=request.user, projekt=project)
        context['scrum_master'] = scrum_master
    except ObjectDoesNotExist:
        scrum_master = None
    try:
        project_owner = ProjectOwner.objects.get(uporabnik=request.user, projekt=project)
        context['project_owner'] = project_owner
    except ObjectDoesNotExist:
        project_owner = None
    if clan is None and project_owner is None and scrum_master is None:
        redirect('/404')

    finished_stories = Zgodba.objects.filter(projekt=project, realizirana=True)
    unfinished_stories = Zgodba.objects.filter(projekt=project, realizirana=False)

    curr_time = datetime.now(pytz.timezone('Europe/Ljubljana'))
    past_sprints = Sprint.objects.filter(projekt=project, zacetni_cas__lte=curr_time).order_by('zacetni_cas')
    if len(past_sprints) > 0:
        past_unfinished_stories = unfinished_stories.filter(sprint__in=past_sprints)
        context['past_unfinished_stories'] = (
            {
                'zgodba': story,
                'naloge_dokoncane': Naloga.objects.filter(zgodba=story, status=Naloga.FINISHED).count(),
                'naloge_vse': Naloga.objects.filter(zgodba=story).count()
            }
            for story in past_unfinished_stories
        )

        rest_unfinished_stories = unfinished_stories.exclude(sprint__in=past_sprints)
        context['rest_unfinished_stories'] = ({'zgodba': story} for story in rest_unfinished_stories)

        context['finished_stories'] = [
            {
                'sprint': sprint,
                'zgodbe': [{'zgodba': story} for story in finished_stories.filter(sprint=sprint)]
                if finished_stories.filter(sprint=sprint).count() != 0 else None
            }
            for sprint in past_sprints
        ]

    try:
        curr_sprint = Sprint.objects.get(projekt=project, zacetni_cas__lte=curr_time, koncni_cas__gte=curr_time)
        context['current_sprint'] = curr_sprint
        context['current_unfinished_stories'] = (
            {
                'zgodba': story,
                'naloge_dokoncane': Naloga.objects.filter(zgodba=story, status=Naloga.FINISHED).count(),
                'naloge_vse': Naloga.objects.filter(zgodba=story).count()
            }
            for story in unfinished_stories.filter(sprint=curr_sprint)
        )
    except Sprint.DoesNotExist:
        pass

    return render(request, "product_backlog/product_backlog.html", context)


def missing(request):
    return render(request, "404.html")


@login_required
@restrict_SM
def create_new_sprint(request):
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('sprint_list')
    else:
        form = SprintForm()
    return render(request, 'sprint_form.html', {'form': form, 'create': True})


@login_required
def sprint_list(request, project_id=None):
    cas_now = datetime.now().timestamp()
    if project_id:
        sprinti = Sprint.objects.filter(projekt_id=project_id)
    else:
        sprinti = Sprint.objects.all()
    projekti = Projekt.objects.all()
    try:
        izbran_projekt = Projekt.objects.get(id=project_id)
    except Projekt.DoesNotExist:
        izbran_projekt = None
    return render(request, 'sprint_list.html', {'sprinti': sprinti, 'projekti': projekti,
                                                'izbran_projekt': izbran_projekt, 'cas': cas_now})


@login_required
@restrict_SM
def edit_sprint(request, sprint_id):
    try:
        instance = get_object_or_404(Sprint, id=sprint_id)
        if instance.zacel():
            raise PermissionDenied
        if request.method == 'POST':
            form = EditSprintForm(request.POST or None, instance=instance)
            if request.user.is_superuser:
                form = EditSprintFormAdmin(request.POST or None, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('sprint_list')
        else:
            form = EditSprintForm(request.POST or None, instance=instance)
            if request.user.is_superuser:
                form = EditSprintFormAdmin(request.POST or None, instance=instance)
        return render(request, 'sprint_form.html', {'form': form, 'sprint': instance, 'create': False})
    except Sprint.DoesNotExist:
        raise Http404

@login_required
@restrict_SM
def delete_sprint(request, id):
    instance = Sprint.objects.get(id=id)
    if instance.zacel():
        raise PermissionDenied
    else:
        instance.delete()
    return redirect("sprint_list")


def project_summary(request, project_id):
    instance = get_object_or_404(Projekt, id=project_id)
    clani = Clan.objects.filter(projekt=instance)
    sprinti = Sprint.objects.filter(projekt=instance)
    scrum_master = ScrumMaster.objects.get(projekt=instance)
    project_owner = ProjectOwner.objects.get(projekt=instance)
    project_posts = Objava.objects.filter(projekt=instance)
    return render(request, 'project_summary.html',
                  {
                      'projekt': instance,
                      'clani': clani,
                      'sprinti': sprinti,
                      'scrum_master': scrum_master,
                      'project_owner': project_owner,
                      'project_posts': project_posts,
                      'post_form': ObjavaForm
                  })


@login_required
def create_new_task(request, story_id):
    project_id = Zgodba.objects.get(id=story_id).projekt_id
    if request.method == "POST":
        form = NalogaForm(request.POST)
        form.fields['clan'].queryset = Clan.objects.filter(projekt_id=project_id)
        if form.is_valid():
            task = form.save(commit=False)
            task.zgodba = Zgodba.objects.get(id=story_id)
            if task.clan:
                task.status = 0
            else:
                task.status = -1
            task.save()
            url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
            return HttpResponse(status=204,
                                headers={
                                    'HX-Trigger': json.dumps({
                                        "tasksListChanged": None,
                                    }),
                                    'HX-Redirect': url
                                })
    else:
        form = NalogaForm(projekt_id=project_id)
        return render(request, 'tasks_form.html', {
            'form': form,
        })


@login_required
def accept_task(request, task_id):
    task = Naloga.objects.get(id=task_id)
    story = Zgodba.objects.get(id=task.zgodba_id)
    clan = Clan.objects.get(projekt_id=story.projekt_id, uporabnik_id=request.user.id)
    task.clan = clan
    task.status = 1
    task.save()
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "taskAccepted": None,
                            }),
                            'HX-Redirect': url
                        })


@login_required
def resign_task(request, task_id):
    task = Naloga.objects.get(id=task_id)
    task.clan = None
    task.status = -1
    task.save()
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "taskResigned": None,
                            }),
                            'HX-Redirect': url
                        })


@login_required
def start_task(request, task_id):
    task = Naloga.objects.get(id=task_id)
    task.status = 0
    task.save()
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "taskStarted": None,
                            }),
                            'HX-Redirect': url
                        })


@login_required
def finish_task(request, task_id):
    task = Naloga.objects.get(id=task_id)
    task.status = 2
    task.save()
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "taskFinished": None,
                            }),
                            'HX-Redirect': url
                        })

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Naloga, pk=pk)
    if request.method == "POST":
        form = NalogaForm(request.POST, instance=task)
        form.fields['clan'].queryset = Clan.objects.filter(projekt_id=task.zgodba.projekt_id)
        if form.is_valid():
            task = form.save(commit=False)
            if task.clan:
                task.status = 0
            else:
                task.status = -1
            task.save()

            url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "tasksListChanged": None,
                    }),
                    'HX-Redirect': url
                }
            )
    else:
        project_id = task.zgodba.projekt_id
        form = NalogaForm(instance=task, projekt_id=project_id)
    return render(request, 'tasks_form.html', {
        'form': form,
        'task': task,
    })

@login_required
def remove_task(request, pk):
    task = get_object_or_404(Naloga, pk=pk)
    task.delete()
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "tasksListChanged": None,
            }),
            'HX-Redirect': url
        })

@login_required
def tasks_list(request, story_id):
    story = get_object_or_404(Zgodba, id=story_id)
    tasks = Naloga.objects.filter(zgodba=story)
    canEdit = True
    canAccept = True
    canCreate = True
    try:
        Clan.objects.get(projekt_id=story.projekt_id, uporabnik_id=request.user.id)
    except Clan.DoesNotExist:
        canEdit = False
        canAccept = False
        canCreate = False

    if not canEdit:
        try:
            canEdit = True
            canAccept = True
            canCreate = True
            ScrumMaster.objects.get(projekt_id=story.projekt_id, uporabnik_id=request.user.id)
        except ScrumMaster.DoesNotExist:
            canEdit = False
            canAccept = False
            canCreate = False

    return render(request, 'tasks_list.html', {
        'tasks': tasks,
        'canEdit': canEdit,
        'canAccept': canAccept,
        'canCreate': canCreate
    })
