from django.core.exceptions import PermissionDenied

from website.models import ScrumMaster


def restricted(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        try:
            ScrumMaster.objects.get(uporabnik=request.user)

            return function(request, *args, **kwargs)
        except ScrumMaster.DoesNotExist:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
