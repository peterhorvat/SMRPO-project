from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms.models import model_to_dict

from website.models import Zgodba, Projekt, Uporabnik, ScrumMaster, ProjectOwner, Clan, Naloga
from website.forms import ZgodbaForm, ZgodbaOpombeForm
from website.decorators import restrict_PO_SM, restrict_PO


class StoriesApi(View):

    @method_decorator(login_required)
    def get(self, request, project_id, story_id=None):
        try:
            project = Projekt.objects.get(pk=project_id)
            user = Uporabnik.objects.get(pk=request.user.id)
            if not is_in_project(user, project):
                return JsonResponse({'Message': f'Uporabnik {user} nima pooblastil.'}, status=403)
        except ObjectDoesNotExist:
            return JsonResponse({'Message': 'Uporabnik ali projekt ne obstaja.'}, status=404)
        if story_id is None:
            stories = Zgodba.objects.filter(projekt=project)
            return JsonResponse({'Message': [model_to_dict(s) for s in stories]}, status=200)
        else:
            try:
                story = Zgodba.objects.get(id=story_id, projekt=project)
                return JsonResponse({'Message': model_to_dict(story)}, status=200)
            except ObjectDoesNotExist:
                return JsonResponse({'Message': 'Zgodba ne obstaja.'}, status=404)

    @method_decorator(login_required)
    @method_decorator(restrict_PO_SM)
    def post(self, request, project_id, story_id=None):
        t = check_credentials(project_id, request.user.id)
        if not isinstance(t, tuple):
            return t
        project, user = t[0], t[1]
        if story_id is None:
            # Create a new story
            story_form = ZgodbaForm(request.POST)
            if not story_form.is_valid():
                return JsonResponse({'Message': story_form.errors}, status=400)
            if not is_name_valid(story_form.cleaned_data['ime'], project):
                return JsonResponse({'Message': 'Zgodba z imenom že obstaja.'}, status=400)
            story_instance = story_form.save(commit=False)
            story_instance.projekt = project
            num = Zgodba.objects.filter(projekt=project).count() + 1 # start with 1
            story_instance.ime = f'#{num} {story_instance.ime}'
            story_instance.save()
            return JsonResponse({'Message': model_to_dict(story_instance)}, status=201)
        else:
            try:
                story = Zgodba.objects.get(pk=story_id)
            except ObjectDoesNotExist:
                return JsonResponse({'Message': f'Zgodba z {story_id} ne obstaja.'}, status=404)
            if story.realizirana or story.sprint is not None:
                return JsonResponse({'Message': 'Zgodbe ni mogoče spreminjati!'}, status=400)
            story_form = ZgodbaForm(request.POST, instance=story)
            if not story_form.is_valid():
                return JsonResponse({'Message': story_form.errors}, status=400)
            if not is_name_valid(story_form.cleaned_data['ime'], project, story_id):
                return JsonResponse({'Message': 'Zgodba z imenom že obstaja!'}, status=400)

            story_instance = story_form.save(commit=False)
            story_instance.save()
            return JsonResponse({'Message': model_to_dict(story_instance)}, status=201)

    @method_decorator(login_required)
    @method_decorator(restrict_PO_SM)
    def delete(self, request, project_id, story_id=None):
        if story_id is None:
            return JsonResponse({'Message': "Manjka ID zgodbe."}, status=404)
        else:
            t = check_credentials(project_id, request.user.id)
            if not isinstance(t, tuple):
                return t
            try:
                story = Zgodba.objects.get(id=story_id)
                if story.realizirana or story.sprint is not None:
                    return JsonResponse({'Message': 'Zgodbe ni mogoče izbrisati!'}, status=400)
                story.delete()
                return JsonResponse({'Message': 'Izbrisano'}, status=204)
            except ObjectDoesNotExist:
                return JsonResponse({'Message': 'Zgodba ne obstaja.'}, status=404)
            except IntegrityError as e:
                return JsonResponse({'Message': f'Integrity error: {str(e)}'}, status=403)


class StoriesConfirmApi(View):

    @method_decorator(login_required)
    @method_decorator(restrict_PO)
    def post(self, request, project_id, story_id):
        try:
            project = Projekt.objects.get(id=project_id)
        except Projekt.DoesNotExist:
            return JsonResponse({'Message': 'Projekt ne obstaja!'}, status=404)
        try:
            story = Zgodba.objects.get(projekt=project, id = story_id)
            finished_tasks = Naloga.objects.filter(zgodba=story, status=Naloga.FINISHED).count()
            all_tasks = Naloga.objects.filter(zgodba=story).count()
            if story.realizirana:
                return JsonResponse({'Message': 'Zgodba je že realizirana!'}, status=400)
            if all_tasks == 0:
                return JsonResponse({'Message': 'Zgodba nima nobenih nalog!'}, status=400)
            if finished_tasks != all_tasks:
                return JsonResponse({'Message': 'Vse naloge še niso dokončane!'}, status=400)
            story.realizirana = True
            story.save()
            return JsonResponse({'Message': 'Success.'}, status=200)
        except Zgodba.DoesNotExist:
            return JsonResponse({'Message': 'Zgodba ne obstaja!'}, status=404)


class StoriesRejectApi(View):

    @method_decorator(login_required)
    @method_decorator(restrict_PO)
    def post(self, request, project_id, story_id):
        try:
            project = Projekt.objects.get(id=project_id)
        except Projekt.DoesNotExist:
            return JsonResponse({'Message': 'Projekt ne obstaja!'}, status=404)
        try:
            story = Zgodba.objects.get(projekt=project, id=story_id)
        except Zgodba.DoesNotExist:
            return JsonResponse({'Message': 'Zgodba ne obstaja!'}, status=404)
        if story.sprint is None:
            return JsonResponse({'Message': 'Zgodba ni dodeljena nobenemu sprintu!'}, status=400)
        if story.realizirana:
            return JsonResponse({'Message': 'Zgodba je že dokončana!'}, status=400)
        opombeForm = ZgodbaOpombeForm(request.POST, instance=story)
        if opombeForm.is_valid():
            story.opombe = opombeForm.cleaned_data['opombe']
            story.sprint = None
            story.save()
            return JsonResponse({'Message': 'Zgodba uspešno zavrnjena.'}, status=200)
        else:
            return JsonResponse({'Message': 'Nepravilno vnešene opombe!'}, status=400)



def check_credentials(project_id, user_id):
    try:
        project = Projekt.objects.get(pk=project_id)
        user = Uporabnik.objects.get(pk=user_id)
        return project, user
    except ObjectDoesNotExist:
        return JsonResponse({'Message': 'Projekt ali uporabnik ne obstaja.'}, status=404)


def is_in_project(user, project):
    try:
        return ScrumMaster.objects.filter(projekt=project, uporabnik=user).count() == 1 \
            or ProjectOwner.objects.filter(projekt=project, uporabnik=user).count() == 1 \
            or Clan.objects.filter(projekt=project, uporabnik=user).count() > 0
    except Exception:
        return False


def is_name_valid(name, project, story_id = None):
    split_name = name.split(" ")
    if split_name[0][0] == '#':
        split_name.pop(0)

    stories = Zgodba.objects.filter(projekt=project) if story_id is None else \
        Zgodba.objects.filter(projekt=project).exclude(pk=story_id)

    for s in stories:
        splinted = s.ime.split()
        if splinted[0][0] == '#':
            splinted.pop(0)
        if len(split_name) == len(splinted):
            if all((splinted[i].lower() == split_name[i].lower() for i in range(len(splinted)))):
                return False
    return True
