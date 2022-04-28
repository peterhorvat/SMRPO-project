from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from api.helper import is_in_project
from website.forms import ObjavaForm, KomentarForm
from website.models import Projekt, Uporabnik, Objava, Clan


class ProjectPosts(View):

    @method_decorator(login_required)
    def post(self, request, project_id):
        try:
            project = Projekt.objects.get(pk=project_id)
        except Projekt.DoesNotExist:
            return JsonResponse({'Message': 'Projekt ne obstaja!'}, status=404)
        user = Uporabnik.objects.get(pk=request.user.id)
        if not is_in_project(user, project):
            return JsonResponse({'Message': 'Uporabnik ni del projekta!'}, status=404)
        objava_form = ObjavaForm(request.POST)
        if not objava_form.is_valid():
            return JsonResponse({'Message': objava_form.errors}, status=400)
        objava_instance = objava_form.save(commit=False)
        objava_instance.uporabnik = user
        objava_instance.projekt = project
        objava_instance.save()
        return JsonResponse({'Message': model_to_dict(objava_instance)}, status=201)


class CommentPost(View):
    @method_decorator(login_required)
    def post(self, request, project_id, post_id):
        try:
            project = Projekt.objects.get(pk=project_id)
        except Projekt.DoesNotExist:
            return JsonResponse({'Message': 'Projekt ne obstaja!'}, status=404)
        user = Uporabnik.objects.get(pk=request.user.id)
        if not is_in_project(user, project):
            return JsonResponse({'Message': 'Uporabnik ni del projekta!'}, status=404)
        objava = Objava.objects.get(id=post_id)
        comment_form = KomentarForm(request.POST)
        if not comment_form.is_valid():
            return JsonResponse({'Message': comment_form.errors}, status=400)
        comment_instance = comment_form.save(commit=False)
        comment_instance.clan = Clan.objects.get(projekt=project, uporabnik=request.user)
        comment_instance.objava = objava

        comment_instance.save()
        return JsonResponse({'Message': model_to_dict(comment_instance)}, status=201)