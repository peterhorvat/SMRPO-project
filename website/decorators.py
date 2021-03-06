from django.core.exceptions import PermissionDenied

from website.models import ScrumMaster, ProjectOwner, Sprint


def restrict_SM(function):
    def wrap(request, project_id, *args, **kwargs):
        # if request.user.is_superuser:
        #     return function(request, *args, **kwargs)
        try:
            ScrumMaster.objects.get(projekt_id=project_id, uporabnik=request.user)

            return function(request, project_id, *args, **kwargs)
        except ScrumMaster.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_PO(function):
    def wrap(request, project_id, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, project_id, *args, **kwargs)
        try:
            ProjectOwner.objects.get(projekt_id=project_id, uporabnik=request.user)

            return function(request, project_id, *args, **kwargs)
        except ProjectOwner.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_PO_SM(function):
    def wrap(request, project_id, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, project_id, *args, **kwargs)
        try:
            ProjectOwner.objects.get(projekt_id=project_id, uporabnik=request.user)
            return function(request, project_id, *args, **kwargs)
        except ProjectOwner.DoesNotExist:
            try:
                ScrumMaster.objects.get(projekt_id=project_id, uporabnik=request.user)
                return function(request, project_id, *args, **kwargs)
            except ScrumMaster.DoesNotExist:
                raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
