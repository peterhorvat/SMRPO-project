from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from website.models import Uporabnik, Projekt, Clan, ProjectOwner, ScrumMaster, Sprint, Zgodba, Naloga, Komentar, Objava, DailyScrum, \
    Dokumentacija, BelezenjeCasa, Besedila
from website.forms import UporabnikChangeForm, UporabnikCreationForm


class UporabnikAdmin(UserAdmin):
    add_form = UporabnikCreationForm
    form = UporabnikChangeForm
    model = Uporabnik
    list_display = ['username', 'first_name', 'last_name', 'email', 'otp_auth']
    search_fields = ('username',)


class ProjektAdmin(admin.ModelAdmin):
    search_fields = ('ime',)
    list_display = ('ime', )
    # list_filter = []


class ClanAdmin(admin.ModelAdmin):
    search_fields = ('uporabnik', )
    list_display = ['projekt', 'uporabnik']
    # list_filter = []


class MasterAdmin(admin.ModelAdmin):
    search_fields = ('uporabnik', )
    list_display = ['projekt', 'uporabnik']
    # list_filter = []


class OwnerAdmin(admin.ModelAdmin):
    search_fields = ('uporabnik', )
    list_display = ['projekt', 'uporabnik']
    # list_filter = []


class SprintAdmin(admin.ModelAdmin):
    search_fields = ('ime', )
    list_display = ['ime', 'projekt', 'zacetni_cas', 'koncni_cas', 'hitrost']
    # list_filter = []


class ZgodbaAdmin(admin.ModelAdmin):
    search_fields = ('ime', )
    list_display = ['projekt', 'ime', 'vsebina', 'sprejemni_testi', 'poslovna_vrednost', 'prioriteta', 'opombe']
    # list_filter = []


class NalogaAdmin(admin.ModelAdmin):
    search_fields = ('ime', )
    list_display = ['ime', 'clan', 'zgodba', 'opis', 'cas', 'status']
    # list_filter = []


class KomentarAdmin(admin.ModelAdmin):
    search_fields = ('uporabnik',)
    list_display = ['uporabnik', 'objava', 'besedilo']
    # list_filter = []


class ObjavaAdmin(admin.ModelAdmin):
    search_fields = ('uporabnik',)
    list_display = ['uporabnik', 'projekt', 'naslov']
    # list_filter = []


class DailyScrumAdmin(admin.ModelAdmin):
    search_fields = ('projekt',)
    list_display = ['have_done', 'will_do', 'problems', 'projekt']
    # list_filter = []


class DokumentacijaAdmin(admin.ModelAdmin):
    search_fields = ('naslov',)
    list_display = ['naslov', 'projekt', 'vsebina', 'tip']
    # list_filter = []


# class BelezenjeCasaAdmin(admin.ModelAdmin):
#     search_fields = ('clan',)
#     list_display = ['clan', 'zacetek', 'ure', 'presoja']
#     # list_filter = []


class BesedilaAdmin(admin.ModelAdmin):
    search_fields = ('naslov',)
    list_display = ['naslov', 'tekst', 'uporaba', 'slug']
    # list_filter = []


admin.site.register(Uporabnik, UporabnikAdmin)
admin.site.register(Projekt, ProjektAdmin)
admin.site.register(Clan, ClanAdmin)
admin.site.register(ProjectOwner, OwnerAdmin)
admin.site.register(ScrumMaster, MasterAdmin)
admin.site.register(Sprint, SprintAdmin)
admin.site.register(Zgodba, ZgodbaAdmin)
admin.site.register(Naloga, NalogaAdmin)
admin.site.register(Komentar, KomentarAdmin)
admin.site.register(Objava, ObjavaAdmin)
admin.site.register(DailyScrum, DailyScrumAdmin)
admin.site.register(Dokumentacija, DokumentacijaAdmin)
admin.site.register(BelezenjeCasa)
admin.site.register(Besedila, BesedilaAdmin)
