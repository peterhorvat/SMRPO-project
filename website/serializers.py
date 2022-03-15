from rest_framework import serializers

from website.models import Projekt, Clan, Sprint, Zgodba, Naloga, Komentar, Objava, DailyScrum, Dokumentacija, \
    BelezenjeCasa


class ProjektSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projekt
        fields = '__all__'
        # fields = ['ime']


class ClanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clan
        fields = '__all__'
        # fields = ['projekt', 'vloga', 'uporabnik']


class SprintSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sprint
        fields = '__all__'
        # fields = ['ime', 'projekt', 'zacetni_cas', 'koncni_cas', 'hitrost']


class ZgodbaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zgodba
        fields = '__all__'
        # fields = ['projekt', 'ime', 'vsebina', 'sprejemni_testi', 'poslovna_vrednost', 'prioriteta', 'opombe']


class NalogaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Naloga
        fields = '__all__'
        # fields = ['ime', 'clan', 'zgodba', 'opis', 'cas', 'status']


class KomentarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Komentar
        fields = '__all__'
        # fields = ['clan', 'zgodba', 'besedilo']


class ObjavaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objava
        fields = '__all__'
        # fields = ['naslov', 'clan']


class DailyScrumSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyScrum
        fields = '__all__'
        # fields = ['have_done', 'will_do', 'problems', 'projekt']


class DokumentacijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dokumentacija
        fields = '__all__'
        # fields = ['naslov', 'projekt', 'vsebina', 'tip']


class BelezenjeCasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BelezenjeCasa
        fields = '__all__'
        # fields = ['clan', 'zacetek', 'konec', 'presoja']





