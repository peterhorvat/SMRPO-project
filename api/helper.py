from website.models import ScrumMaster, ProjectOwner, Clan


def is_in_project(user, project):
    try:
        return ScrumMaster.objects.filter(projekt=project, uporabnik=user).count() == 1 \
            or ProjectOwner.objects.filter(projekt=project, uporabnik=user).count() == 1 \
            or Clan.objects.filter(projekt=project, uporabnik=user).count() > 0
    except Exception:
        return False
