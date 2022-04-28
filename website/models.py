from datetime import datetime, date

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from django.db import models
from autoslug import AutoSlugField
from ckeditor.fields import RichTextField


class Uporabnik(AbstractUser):
    username = models.CharField(max_length=30, unique=True, editable=True, verbose_name="Uporabniško ime")
    first_name = models.CharField(max_length=30, verbose_name="Ime", editable=True)
    last_name = models.CharField(max_length=150, verbose_name="Priimek", editable=True)
    email = models.EmailField(unique=True, verbose_name="e-mail")
    slug = AutoSlugField(max_length=255, populate_from='username', default="", null=True, blank=True,
                         verbose_name="Username slug")
    otp_auth = models.BooleanField(default=True, verbose_name="Zahtevana OTP avtentikacija")
    previous_login = models.DateTimeField(null=True, blank=True, verbose_name="Prejšnja prijava")
    USERNAME_FIELD = "username"

    def __str__(self):
        return f"[{self.username}]: {self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Uporabniki"
        verbose_name = "Uporabnik"


def update_last_and_previous_login(sender, user, **kwargs):
    user.previous_login = user.last_login
    user.last_login = timezone.now()
    user.save(update_fields=["previous_login", "last_login"])


user_logged_in.disconnect(update_last_login, dispatch_uid="update_last_login")
user_logged_in.connect(update_last_and_previous_login, dispatch_uid="update_last_and_previous_login")


class Projekt(models.Model):
    ime = models.CharField(max_length=255, verbose_name="Ime projekta")
    opis = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Projekti"
        verbose_name = "Projekt"

    def __str__(self):
        return f"{self.ime}"


class Clan(models.Model):
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    uporabnik = models.ForeignKey(Uporabnik, on_delete=models.CASCADE, verbose_name="Uporabnik")

    def __str__(self):
        return f"[{self.uporabnik}]: {self.projekt}"

    class Meta:
        verbose_name_plural = "Člani"
        verbose_name = "Član"


class ScrumMaster(models.Model):
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    uporabnik = models.ForeignKey(Uporabnik, on_delete=models.CASCADE, verbose_name="Uporabnik")

    def __str__(self):
        return f"[{self.uporabnik}]: {self.projekt}"

    class Meta:
        verbose_name_plural = "Scrum Master"
        verbose_name = "Scrum Master"
        unique_together = [["projekt", "uporabnik"]]


class ProjectOwner(models.Model):
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    uporabnik = models.ForeignKey(Uporabnik, on_delete=models.CASCADE, verbose_name="Uporabnik")

    def __str__(self):
        return f"[{self.uporabnik}]: {self.projekt}"

    class Meta:
        verbose_name_plural = "Project Owner"
        verbose_name = "Project Owner"
        unique_together = [["projekt", "uporabnik"]]


# Nov sprint se ne more začet dokler se ne konča prejšnji
class Sprint(models.Model):
    ime = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ime sprinta")
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    zacetni_cas = models.DateField(verbose_name="Začetni čas sprinta")
    koncni_cas = models.DateField(verbose_name="Končni čas sprinta")
    hitrost = models.IntegerField(verbose_name="Predvidena hitrost sprinta")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sprinti"
        verbose_name = "Sprint"

    def pretekel(self):
        return self.koncni_cas < date.today()

    def bo_pretekel(self):
        razlika = self.koncni_cas - date.today()
        return razlika.days < 2

    def zacel(self):
        return self.zacetni_cas < date.today()

    def __str__(self):
        return f"[{self.projekt}] {self.ime}"


class Zgodba(models.Model):
    COULD_HAVE = 3
    SHOULD_HAVE = 2
    MUST_HAVE = 1
    WONT_HAVE = -1
    PRIORITETE = (
        (COULD_HAVE, 'Could have'),
        (SHOULD_HAVE, 'Should have'),
        (MUST_HAVE, 'Must have'),
        (WONT_HAVE, "Won't have this time")
    )
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, verbose_name="Sprint", null=True)
    ime = models.CharField(max_length=255, verbose_name="Ime zgodbe")
    vsebina = RichTextField(verbose_name="Vsebina zgodbe")
    sprejemni_testi = RichTextField(verbose_name="Sprejemni testi zgodbe")
    poslovna_vrednost = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                            verbose_name="Poslovna vrednost zgodbe")
    ocena = models.IntegerField(verbose_name="Časovna ocena", default=0)
    prioriteta = models.IntegerField(choices=PRIORITETE, verbose_name="Prioriteta")
    opombe = RichTextField(blank=True, verbose_name="Opombe zgodbe", default="")
    realizirana = models.BooleanField(default=False, verbose_name="Realizirana zgodba")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zgodbe"
        verbose_name = "Zgodba"

    def __str__(self):
        return f"[{self.projekt}] {self.ime}"


class Naloga(models.Model):
    NOT_ASSIGNED = -1
    PENDING = 0
    ACCEPTED = 1
    FINISHED = 2
    PRIORITETE = (
        (NOT_ASSIGNED, 'Nedodeljena'),
        (PENDING, 'Dodeljena'),
        (ACCEPTED, 'Aktivna'),
        (FINISHED, 'Zaključena'),
    )

    ime = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ime naloge")
    clan = models.ForeignKey(Clan, null=True, blank=True,unique=False, on_delete=models.CASCADE, verbose_name="Član")
    zgodba = models.ForeignKey(Zgodba, on_delete=models.CASCADE,  verbose_name="Zgodba")
    opis = RichTextField(verbose_name="Opis naloge")
    cas = models.IntegerField(verbose_name="Ocena časa")
    status = models.IntegerField(choices=PRIORITETE, verbose_name="Status naloge")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Naloge"
        verbose_name = "Naloga"
        # unique_together = ["clan", "zgodba"]

    def __str__(self):
        return f"[{self.zgodba}:{self.clan}] {self.ime}"


class Objava(models.Model):
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    naslov = models.CharField(max_length=255, verbose_name="Naslov objave")
    uporabnik = models.ForeignKey(Uporabnik, on_delete=models.CASCADE, verbose_name="Uporabnik")
    vsebina = RichTextField(verbose_name="Vsebina objave")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Objave"
        verbose_name = "Objava"

    def __str__(self):
        return f"[{self.clan}] {self.naslov}"


class Komentar(models.Model):
    uporabnik = models.ForeignKey(Uporabnik, null=True, on_delete=models.CASCADE, verbose_name="Uporabnik")
    objava = models.ForeignKey(Objava, null=True, on_delete=models.CASCADE, verbose_name="Objava")
    besedilo = RichTextField(verbose_name="Vsebina komentarja")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Komentarji"
        verbose_name = "Komentar"

    def __str__(self):
        return f"[{self.uporabnik}:{self.objava}]"


# Je rekel da mora biti nujno ločeno ker je "svoja stvar"
class DailyScrum(models.Model):
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    have_done = RichTextField(verbose_name="What have you done since the last meeting?")
    will_do = RichTextField(verbose_name="What are you planning to do until next meeting?")
    problems = RichTextField(verbose_name="Have you experienced any problems or issues?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "DailyScrumI"
        verbose_name = "DailyScrum"


class Dokumentacija(models.Model):
    UPORABNISKA = 0
    ADMINISTRATORSKA = 1
    RAZVIJALSKA = 2
    TIPI = (
        (UPORABNISKA, 'Uporabniška'),
        (ADMINISTRATORSKA, 'Administratorska'),
        (RAZVIJALSKA, 'Razvijalska')
    )

    naslov = models.CharField(max_length=255, null=True, blank=True, verbose_name="Naslov dokumentacije")
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    vsebina = RichTextField(verbose_name="Vsebina"),
    tip = models.IntegerField(choices=TIPI, verbose_name="Tip dokumentacije")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Dokumentacije"
        verbose_name = "Dokumentacija"

    def __str__(self):
        return f"[{self.projekt}:{self.tip}] {self.naslov}"


# NOT SURE KJE BOMO TO RABILI HAHA
class BelezenjeCasa(models.Model):
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, verbose_name="Član")
    naloga = models.ForeignKey(Naloga, on_delete=models.CASCADE, verbose_name="Naloga")
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, verbose_name="Sprint")
    zacetek = models.DateTimeField(verbose_name="Čas začetka")
    ure = models.IntegerField(verbose_name="Ure")
    presoja = models.CharField(max_length=255, verbose_name="Končna presoja")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zabeležen čas"
        verbose_name = "Beleženja časa"

    def __str__(self):
        return f"[{self.naloga}:{self.clan}]"


class Besedila(models.Model):
    tekst = RichTextField(verbose_name="Vsebina besedila")
    naslov = models.CharField(max_length=50, verbose_name="Naslov besedila")
    uporaba = models.CharField(max_length=255, verbose_name="Uporaba besedila",
                               help_text="Kje točno se uporablja besedilo")
    slug = AutoSlugField(max_length=255, populate_from='naslov', default="", verbose_name="Slug Besedila")

    class Meta:
        verbose_name = "Privezo besedilo"
        verbose_name_plural = "Privzeta besedila"

    def __str__(self):
        return f'{self.naslov}'


class PastSprints(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.DO_NOTHING, verbose_name="Pretekli Sprint")
    zgodba = models.ForeignKey(Zgodba, on_delete=models.DO_NOTHING, verbose_name="Zgodba")

