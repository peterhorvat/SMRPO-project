import json
from datetime import datetime, timedelta, date
import pytz

import django_otp
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from .decorators import restrict_SM
from .forms import UserLoginForm, CreateNewProjectForm, OTPForm, ZgodbaForm, UporabnikChangeForm, SprintForm, \
    EditSprintForm, NalogaForm, ZgodbaOpombeForm, ObjavaForm, EditSprintFormTekoci, KomentarForm, ZgodbaOcenaForm
from .models import Uporabnik, Projekt, Zgodba, Clan, ProjectOwner, ScrumMaster, Sprint, Naloga, Objava, Komentar, \
    BelezenjeCasa, PastSprints
from itertools import filterfalse


@login_required
def landing_page(request):
    if request.user.is_superuser:
        projekti = Projekt.objects.all()
    else:
        user = Uporabnik.objects.get(pk=request.user.id)
        projekti = list(set([i.projekt for i in Clan.objects.filter(uporabnik=user).iterator()] \
                            + [i.projekt for i in ScrumMaster.objects.filter(uporabnik=user).iterator()] \
                            + [i.projekt for i in ProjectOwner.objects.filter(uporabnik=user).iterator()]))

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
    curr_time = date.today()
    # try:
    #    curr_sprint = Sprint.objects.get(projekt=project, zacetni_cas__lte=curr_time, koncni_cas__gte=curr_time)
    # except Sprint.DoesNotExist:
    #    curr_sprint = None
    stories = Zgodba.objects.filter(projekt=project)
    sprint_backlog_stories = []
    for story in stories:
        if story.sprint:
            if story.sprint.zacetni_cas <= date.today() <= story.sprint.koncni_cas and not story.realizirana:
                sprint_backlog_stories.append(story)
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
        'zgodbe': sprint_backlog_stories,
        'clan': clan,
        'scrum_master': scrum_master,
        'product_owner': product_owner,
        'form': ZgodbaForm(),
    }
    return render(request=request, template_name="sprint_backlog.html", context=context)


@login_required
def edit_project(request, project_id):
    projekt = Projekt.objects.get(pk=project_id)
    project_owner = ProjectOwner.objects.get(projekt=projekt)
    scrum_master = ScrumMaster.objects.get(projekt=projekt)
    exclude = {str(project_owner.uporabnik.id): str(project_owner.uporabnik.username), str(scrum_master.uporabnik.id): scrum_master.uporabnik.username}
    clani = [i.uporabnik.id for i in Clan.objects.all().filter(projekt=project_id)]
    to_delete = {str(i.uporabnik.id): i.uporabnik.username for i in Clan.objects.filter(projekt_id=project_id)}
    available_members = {str(i.id): i.username for i in Uporabnik.objects.exclude(id__in=clani) if ProjectOwner.objects.filter(projekt_id=project_id).first().uporabnik.id != i.id}
    print(available_members)
    if request.method == "GET":
        uporabniki = {str(i["id"]): str(i["username"]) for i in map(lambda x: {"id": x.id, "username": x.username}, list(Uporabnik.objects.all()))}
        clani_projekta = {str(i.uporabnik.id): i.uporabnik.username for i in Clan.objects.filter(projekt_id=project_id)}
        vsi_sodelujoci = set()
        for i in clani_projekta:
            vsi_sodelujoci.add(int(i))
        vsi_sodelujoci.add(int(project_owner.uporabnik.id))
        vsi_sodelujoci.add(int(scrum_master.uporabnik.id))
        vsi_sodelujoci = {int(i.id): i.username for i in Uporabnik.objects.filter(id__in=list(vsi_sodelujoci))}
        return render(request, "edit_project_page.html",
                      {"projekt_ime": projekt.ime, "projekt_opis": projekt.opis, "id": project_id,
                       "form": CreateNewProjectForm(), "uporabniki": json.dumps(uporabniki), "možni_uporabniki": available_members,
                       "clani_projekta": vsi_sodelujoci,
                       "trenutne_vodje": exclude,
                       "izbris": to_delete
                       })
    else:
        if request.POST["ime"] != projekt.ime:
            if len(Projekt.objects.filter(ime=request.POST["ime"])) == 0:
                projekt.ime = request.POST["ime"]
            else:
                return JsonResponse({"data": "Ta ime že obstaja !", "status": 400})
        projekt.opis = request.POST["opis"]
        projekt.save()
        return redirect("/")


def add_new_member(request, project_id):
    if request.method == "POST":
        if Clan.objects.filter(uporabnik_id=request.POST["id"], projekt_id=project_id):
            return HttpResponse(status=400, content="Ta uporabnik je že prisoten na projektu.")
        if ProjectOwner.objects.filter(uporabnik_id=request.POST["id"], projekt_id=project_id):
            return HttpResponse(status=400, content="Uporabnik ne mora biti product owner in sodelovati v razvojni ekipi hkrati.")
        new_member = Clan(projekt_id=project_id, uporabnik=Uporabnik.objects.get(pk=request.POST["id"]))
        new_member.save()
        return HttpResponse(status=200, content="Uporabnik je bil uspešno dodan.")


def switch_roles(request, project_id):
    who_to_switch = request.POST["switch1"].split("&")
    with_whom_switch = int(request.POST["switch2"])
    if who_to_switch[1] == '1':
        current = ProjectOwner.objects.get(projekt_id=project_id)
        new_owner = Uporabnik.objects.get(pk=with_whom_switch)
        if current.uporabnik.id == new_owner.id:
            return HttpResponse(status=200, content="Menjava uporabnika samega s sabo")
        scrum_master = ScrumMaster.objects.filter(uporabnik=new_owner, projekt_id=project_id).first()
        if scrum_master is not None:
            scrum_master.uporabnik = current.uporabnik
            clan = Clan.objects.filter(projekt_id=project_id, uporabnik=scrum_master.uporabnik)
            if len(clan) > 0:
                for i in Naloga.objects.filter(clan=Clan.objects.get(projekt_id=project_id, uporabnik=scrum_master.uporabnik)):
                    i.status = Naloga.NOT_ASSIGNED
            clan.delete()
            current.uporabnik = new_owner
            scrum_master.save()
            current.save()
            return HttpResponse(status=200, content="Uspešna menjava project ownerja in scrum masterja.")
        else:
            clan = Clan.objects.filter(projekt_id=project_id, uporabnik=new_owner)
            if len(clan) > 0:
                for i in Naloga.objects.filter(clan=Clan.objects.get(projekt_id=project_id, uporabnik=new_owner)):
                    i.status = Naloga.NOT_ASSIGNED
            clan.delete()
            current.uporabnik = new_owner
            current.save()
            return HttpResponse(status=200, content="Uspešna menjava project ownerja in team memberja.")
    if who_to_switch[1] == '2':
        current = ScrumMaster.objects.get(projekt_id=project_id)
        new_owner = Uporabnik.objects.get(pk=with_whom_switch)
        if current.uporabnik.id == new_owner.id:
            return HttpResponse(status=200, content="Menjava uporabnika samega s sabo")
        clan = Clan.objects.filter(projekt_id=project_id, uporabnik=new_owner)
        if len(clan) > 0:
            for i in Naloga.objects.filter(clan=Clan.objects.get(projekt_id=project_id, uporabnik=current.uporabnik)):
                i.status = Naloga.NOT_ASSIGNED
            clan.uporabnik = current
            current.uporabnik = new_owner
            clan.save()
            current.save()
            return HttpResponse(status=200, content="Uspešna menjava scrum masterja in team memberja.")
        else:
            previous_owner = ProjectOwner.objects.get(projekt_id=project_id)
            previous_owner.uporabnik = current.uporabnik
            current.uporabnik = new_owner
            previous_owner.save()
            current.save()
            return HttpResponse(status=200, content="Uspešna menjava scrum masterja in project ownerja.")
    return HttpResponse(status=400, content="Te menjave ni mogoče izvest.")


def delete_member(request, project_id, member_id):
    if request.method == "POST":
        if request.user.is_superuser or len(ScrumMaster.objects.get(pk=request.user.id, projekt_id=project_id)) > 0:
            clan = Clan.objects.get(uporabnik_id=member_id, projekt_id=project_id)
            for i in Naloga.objects.filter(clan=clan):
                i.status = Naloga.NOT_ASSIGNED
            clan.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403, content="Nimate pravice za to akcijo.")


def checkIfExists(users):
    pass


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


def get_tasks_for_stories(stories):
    r = []
    for story in stories:
        tasks = Naloga.objects.filter(zgodba=story)
        finished_tasks = tasks.filter(status=Naloga.FINISHED).count()
        story_dict = {
            'zgodba': story,
            'naloge_dokoncane': finished_tasks,
            'naloge_vse': tasks.count()
        }
        r.append(story_dict)
    return r


def get_story_objects(stories, check_tasks=True):
    r = []
    for story in stories:
        story_object = {'zgodba': story}
        if check_tasks:
            story_object['naloge_dokoncane'] = Naloga.objects.filter(zgodba=story, status=Naloga.FINISHED).count()
            story_object['naloge_vse'] = Naloga.objects.filter(zgodba=story).count()
        story_object['work_done'] = get_work_for_story(story)
        r.append(story_object)
    return r


def get_work_for_story(story):
    work = []
    past_sprints = PastSprints.objects.filter(zgodba=story)
    all_sprints = list(set([story.sprint] + [ps.sprint for ps in past_sprints]))
    for sprint in all_sprints:
        work.append(get_work_for_story_sprint(story, sprint))
    return list(filter(lambda w: w is not None, work))


def get_work_for_story_sprint(story, sprint):
    if sprint is None:
        return None
    story_tasks = Naloga.objects.filter(zgodba=story)
    vsota_ur = BelezenjeCasa.objects.filter(naloga__in=story_tasks, sprint=sprint).aggregate(Sum('ure'))['ure__sum']
    return {
        'sprint': sprint,
        'work': vsota_ur
    }


def get_sprint_story_objects(sprints, stories):
    r = []
    for sprint in sprints:
        sprint_object = {'sprint': sprint}
        stories_in_sprint = stories.filter(sprint=sprint)
        if stories_in_sprint.count() > 0:
            sprint_object['zgodbe'] = get_story_objects(stories_in_sprint)
        r.append(sprint_object)
    return r


@login_required
def product_backlog(request, project_id):
    project = get_object_or_404(Projekt, pk=project_id)
    context = {
        'projekt': project,
        'story_form': ZgodbaForm,
        'opombe_form': ZgodbaOpombeForm,
        'ocena_form': ZgodbaOcenaForm
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
    past_sprints = Sprint.objects.filter(projekt=project, zacetni_cas__lt=curr_time, koncni_cas__lt=curr_time).order_by('zacetni_cas')
    future_sprints = Sprint.objects.filter(projekt=project, zacetni_cas__gt=curr_time, koncni_cas__gt=curr_time).order_by('zacetni_cas')

    context['past_unfinished_stories'] = get_story_objects(unfinished_stories.filter(sprint__in=past_sprints))
    context['future_unfinished_stories'] = get_story_objects(
        unfinished_stories.filter(sprint__in=future_sprints), check_tasks=False)
    context['rest_unfinished_stories'] = get_story_objects(
        unfinished_stories.exclude(sprint__isnull=False), check_tasks=False)

    context['finished_stories'] = get_sprint_story_objects(past_sprints, finished_stories)

    try:
        curr_sprint = Sprint.objects.get(projekt=project, zacetni_cas__lte=curr_time, koncni_cas__gte=curr_time)
        context['current_sprint'] = curr_sprint

        context['current_unfinished_stories'] = get_story_objects(unfinished_stories.filter(sprint=curr_sprint))
        context['finished_stories'] += get_sprint_story_objects([curr_sprint], finished_stories)
        try:
            vsota_ocen = Zgodba.objects.filter(sprint=curr_sprint).aggregate(Sum('ocena'))["ocena__sum"]
            context['sum_zgodb'] = vsota_ocen
            context['sum_zgodb_frac'] = (vsota_ocen / curr_sprint.hitrost) * 100
        except Exception:
            context['sum_zgodb'] = 0
            context['sum_zgodb_frac'] = 0.0
    except Sprint.DoesNotExist:
        context['sum_zgodb'] = 0
        context['sum_zgodb_frac'] = 0.0

    return render(request, "product_backlog/product_backlog.html", context)


def missing(request):
    return render(request, "404.html")


@login_required
@restrict_SM
def create_new_sprint(request, project_id):
    if request.method == 'POST':
        form = SprintForm(request.POST, pid=project_id)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.projekt = Projekt.objects.get(id=project_id)
            instance.save()
            return redirect('sprint_list', project_id)
    else:
        form = SprintForm(pid=project_id)
    return render(request, 'sprint_form.html', {'form': form, 'create': True})


@login_required
def sprint_list(request, project_id):
    cas_now = date.today()
    project = get_object_or_404(Projekt, id=project_id)
    try:
        ScrumMaster.objects.get(projekt=project, uporabnik=request.user)
        isSM = True
    except ScrumMaster.DoesNotExist:
        isSM = False
    sprinti = Sprint.objects.filter(projekt=project).order_by("zacetni_cas")
    return render(request, 'sprint_list.html', {'sprinti': sprinti,
                                                'izbran_projekt': project, 'cas': cas_now,
                                                'isSM': isSM})


@login_required
@restrict_SM
def edit_sprint(request, project_id, sprint_id):
    try:
        instance = get_object_or_404(Sprint, id=sprint_id)
        if request.method == 'POST':
            if instance.zacel():
                form = EditSprintFormTekoci(request.POST or None, instance=instance)
            else:
                form = EditSprintForm(request.POST or None, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('sprint_list', project_id)
        else:
            if instance.zacel():
                form = EditSprintFormTekoci(request.POST or None, instance=instance)
            else:
                form = EditSprintForm(request.POST or None, instance=instance)
        return render(request, 'sprint_form.html', {'form': form, 'sprint': instance, 'create': False})
    except Sprint.DoesNotExist:
        raise Http404


@login_required
@restrict_SM
def delete_sprint(request, project_id, sprint_id):
    instance = Sprint.objects.get(id=sprint_id)
    if instance.zacel():
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
    else:
        instance.delete()
        return HttpResponse(status=status.HTTP_200_OK)


@login_required
@restrict_SM
def stories_to_sprint(request, project_id, sprint_id):
    instance = Sprint.objects.get(id=sprint_id)
    try:
        if request.method == 'POST':
            ids = request.POST["storyIds"].split(",")
            sum_ocen = 0
            for story in Zgodba.objects.filter(id__in=ids):
                sum_ocen += story.ocena
            if sum_ocen > instance.hitrost:
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            for story in Zgodba.objects.filter(id__in=ids):
                story.sprint = instance
                story.save()
        return HttpResponse(status=status.HTTP_200_OK)
    except Exception as e:
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def project_summary(request, project_id):
    instance = get_object_or_404(Projekt, id=project_id)
    clani = Clan.objects.filter(projekt=instance)
    sprinti = Sprint.objects.filter(projekt=instance)
    scrum_master = ScrumMaster.objects.get(projekt=instance)
    project_owner = ProjectOwner.objects.get(projekt=instance)
    project_posts = Objava.objects.filter(projekt=instance)
    komentarji = Komentar.objects.filter(objava__projekt=instance)
    return render(request, 'project_summary.html',
                  {
                      'projekt': instance,
                      'clani': clani,
                      'sprinti': sprinti,
                      'scrum_master': scrum_master,
                      'project_owner': project_owner,
                      'project_posts': project_posts,
                      'post_form': ObjavaForm,
                      'comment_form': KomentarForm,
                      'komentarji': komentarji
                  })


@login_required
def delete_comment(request, project_id, comment_id):
    komentar = Komentar.objects.get(id=comment_id)
    if komentar.uporabnik != request.user:
        raise PermissionDenied
    else:
        komentar.delete()
        return redirect('project_summary', project_id)


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
                task.status = Naloga.PENDING
            else:
                task.status = Naloga.NOT_ASSIGNED
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
    task.status = Naloga.ACCEPTED
    task.save()
    start_timer(request, task_id)
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "taskAccepted": None,
                            }),
                            'HX-Redirect': url
                        })


@login_required
def start_timer(request, task_id):
    print(request.POST)
    task = Naloga.objects.get(id=task_id)
    story = Zgodba.objects.get(id=task.zgodba_id)
    clan = Clan.objects.get(projekt_id=story.projekt_id, uporabnik_id=request.user.id)
    belezenje_casa = BelezenjeCasa.objects.filter(clan=clan, naloga=task).last()
    if belezenje_casa is None:
        BelezenjeCasa(clan=clan, naloga=task, sprint=story.sprint, zacetek=timezone.now(), ure=0).save()
    else:
        belezenje_casa.zacetek = timezone.now()
        belezenje_casa.save()
    return HttpResponse(status=200)


@login_required
def end_timer(request, task_id):
    task = Naloga.objects.get(id=task_id)
    story = Zgodba.objects.get(id=task.zgodba_id)
    clan = Clan.objects.get(projekt_id=story.projekt_id, uporabnik_id=request.user.id)
    belezenje_casa = BelezenjeCasa.objects.filter(clan=clan, naloga=task).last()
    if datetime.now().date() == belezenje_casa.zacetek.date():
        belezenje_casa.ure += timezone.now().hour - belezenje_casa.zacetek.hour
    else:
        belezenje_casa += belezenje_casa.zacetek.hour - timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        BelezenjeCasa(clan=clan, naloga=task, sprint=story.sprint, zacetek=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0),
                      ure=(timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timezone.now()).hour).save()
    belezenje_casa.save()
    return HttpResponse(status=200)


@login_required
def timetable(request):
    user = Uporabnik.objects.get(username=request.user.username)
    return render(request, "timetable.html", {"tasks": BelezenjeCasa.objects.filter(clan__uporabnik=user)})


@login_required
def timetable_update(request, task_id):
    what_to_update = int(request.POST["what"])
    beleziCas = BelezenjeCasa.objects.get(pk=int(task_id))
    if what_to_update == 0:
        if beleziCas.presoja != 0 and int(request.POST["value"]) >= beleziCas.presoja:
            beleziCas.ure += abs(int(request.POST["value"]) - beleziCas.presoja)
            finish_task(request, beleziCas.naloga.id)
        else:
            beleziCas.ure = int(request.POST["value"])
        beleziCas.save()
    else:
        presoja = int(request.POST["value"])
        if presoja > beleziCas.ure:
            beleziCas.presoja = presoja
        elif presoja == beleziCas.ure:
            beleziCas.presoja = presoja
            finish_task(request, beleziCas.naloga.id)
        else:
            return HttpResponse(status=400, content="Presoja ne mora biti manjša kakor že opravljeno število ur.")
        beleziCas.save()
    return HttpResponse(status=200)


@login_required
def resign_task(request, task_id):
    task = Naloga.objects.get(id=task_id)
    task.clan = None
    task.status = Naloga.NOT_ASSIGNED
    task.save()
    end_timer(request, task_id)
    url = "http://" + request.get_host() + "/projects/" + str(task.zgodba.projekt_id) + "/sprint_backlog/"
    return HttpResponse(status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "taskResigned": None,
                            }),
                            'HX-Redirect': url
                        })


@login_required
def finish_task(request, task_id):
    task = Naloga.objects.get(id=task_id)
    task.status = Naloga.FINISHED
    task.save()
    story = Zgodba.objects.get(id=task.zgodba_id)
    clan = Clan.objects.get(projekt_id=story.projekt_id, uporabnik_id=request.user.id)
    end_timer(request, task_id)
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
                task.status = Naloga.PENDING
            else:
                task.status = Naloga.NOT_ASSIGNED
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
            canAccept = False
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
