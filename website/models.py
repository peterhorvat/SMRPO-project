from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from autoslug import AutoSlugField
from ckeditor.fields import RichTextField

# Create your models here.


class Uporabnik(AbstractUser):
    username = models.CharField(max_length=30, unique=True, editable=True, verbose_name="Username")
    first_name = models.CharField(max_length=30, verbose_name="First name")
    last_name = models.CharField(max_length=150, verbose_name="Last name")
    email = models.EmailField(unique=True, verbose_name="e-Mail")
    slug = AutoSlugField(max_length=255, populate_from='username', default="", null=True, blank=True,
                         verbose_name="Username slug")
    otp_auth = models.BooleanField(default=True, verbose_name="Zahtevana OTP avtentikacija")
    USERNAME_FIELD = "username"

    def __str__(self):
        return f"[{self.username}]: {self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Uporabniki"
        verbose_name = "Uporabnik"


class Projekt(models.Model):

    ime = models.CharField(max_length=255, verbose_name="Ime projekta")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Projekti"
        verbose_name = "Projekt"

    def __str__(self):
        return f"{self.ime}"


class Clan(models.Model):
    VLOGA_TYPES = (
        (0, 'Product owner'),
        (1, 'Scrum master'),
        (2, 'Team member'),
    )
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    vloga = models.IntegerField(choices=VLOGA_TYPES, verbose_name="Vloga pri projektu")
    uporabnik = models.ForeignKey(Uporabnik, on_delete=models.CASCADE, verbose_name="Uporabnik")

    def __str__(self):
        return f"[{self.uporabnik}]: {self.projekt}"

    class Meta:
        verbose_name_plural = "Člani"
        verbose_name = "Član"
        unique_together = ["projekt", "vloga"]


# Nov sprint se ne more začet dokler se ne konča prejšnji
class Sprint(models.Model):
    ime = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ime sprinta")
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    zacetni_cas = models.DateTimeField(verbose_name="Začetni čas sprinta")
    koncni_cas = models.DateTimeField(verbose_name="Končni čas sprinta")
    hitrost = models.IntegerField(verbose_name="Predvidena hitrost sprinta")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sprinti"
        verbose_name = "Sprint"

    def __str__(self):
        return f"[{self.projekt}] {self.ime}"


class Zgodba(models.Model):
    PRIORITETE = (
        (3, 'Could have'),
        (2, 'Should have'),
        (1, 'Must have'),
        (-1, "Won't have this time")
    )
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, verbose_name="Projekt")
    ime = models.CharField(max_length=255, verbose_name="Ime zgodbe")
    vsebina = RichTextField(verbose_name="Vsebina zgodbe")
    sprejemni_testi = RichTextField(verbose_name="Sprejemni testi zgodbe")
    poslovna_vrednost = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                            verbose_name="Poslovna vrednost zgodbe")
    prioriteta = models.CharField(max_length=1, choices=PRIORITETE, verbose_name="Vloga pri projektu")
    opombe = RichTextField(verbose_name="Opombe zgodbe")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zgodbe"
        verbose_name = "Zgodba"

    def __str__(self):
        return f"[{self.projekt}] {self.ime}"


class Naloga(models.Model):

    PRIORITETE = (
        (-1, 'Not assigned'),
        (0, 'Pending'),
        (1, 'Accepted'),
        (2, 'Finished'),
    )

    ime = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ime zgodbe")
    clan = models.ForeignKey(Clan, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Član")
    zgodba = models.ForeignKey(Zgodba, on_delete=models.CASCADE, verbose_name="Zgodba")
    opis = RichTextField(verbose_name="Opis naloge")
    cas = models.IntegerField(verbose_name="Ocena časa")
    status = models.IntegerField(choices=PRIORITETE, verbose_name="Status naloge")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Naloge"
        verbose_name = "Naloga"
        unique_together = ["clan", "zgodba"]

    def __str__(self):
        return f"[{self.zgodba}:{self.clan}] {self.ime}"


class Komentar(models.Model):
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, verbose_name="Član")
    zgodba = models.ForeignKey(Zgodba, on_delete=models.CASCADE, verbose_name="Zgodba")
    besedilo = RichTextField(verbose_name="Vsebina komentarja")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Komentarji"
        verbose_name = "Komentar"

    def __str__(self):
        return f"[{self.zgodba}:{self.clan}]"


class Objava(models.Model):
    naslov = models.CharField(max_length=255, null=True, blank=True, verbose_name="Naslov objave")
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, verbose_name="Član")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Objave"
        verbose_name = "Objava"

    def __str__(self):
        return f"[{self.clan}] {self.naslov}"


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
    TIPI = (
        (0, 'Uporabniška'),
        (1, 'Administratorska'),
        (2, 'Razvijalska')
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
    zacetek = models.DateTimeField(verbose_name="Čas začetka")
    konec = models.DateTimeField(verbose_name="Čas konca")
    presoja = models.CharField(max_length=255, verbose_name="Končna presoja")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zabeležen čas"
        verbose_name = "Beleženja časa"
        unique_together = ["clan", "naloga"]

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
