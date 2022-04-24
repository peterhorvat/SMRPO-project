from django.core.exceptions import PermissionDenied

from website.models import ScrumMaster, ProjectOwner


def restrict_SM(function):
    def wrap(request, *args, **kwargs):
        # if request.user.is_superuser:
        #     return function(request, *args, **kwargs)
        try:
            ScrumMaster.objects.get(uporabnik=request.user)

            return function(request, *args, **kwargs)
        except ScrumMaster.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_PO(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        try:
            ProjectOwner.objects.get(uporabnik=request.user)

            return function(request, *args, **kwargs)
        except ProjectOwner.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_PO_SM(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        try:
            ProjectOwner.objects.get(uporabnik=request.user)
            return function(request, *args, **kwargs)
        except ProjectOwner.DoesNotExist:
            try:
                ScrumMaster.objects.get(uporabnik=request.user)
                return function(request, *args, **kwargs)
            except ScrumMaster.DoesNotExist:
                raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
