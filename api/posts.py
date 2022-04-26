from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from api.helper import is_in_project
from website.forms import ObjavaForm
from website.models import Projekt, Uporabnik


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
