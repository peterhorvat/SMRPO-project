from django.contrib.auth.models import AbstractUser
from django.db import models
from autoslug import AutoSlugField
from ckeditor.fields import RichTextField

# Create your models here.


class Uporabnik(AbstractUser):
    username = models.CharField(max_length=30, unique=True, editable=True, verbose_name="Username")
    first_name = models.CharField(max_length=30, verbose_name="First name")
    last_name = models.CharField(max_length=150, verbose_name="Last name")
    email = models.EmailField(unique=True, verbose_name="e-Mail")
    slug = AutoSlugField(max_length=255, populate_from='username', default="", null=True, blank=True, verbose_name="Username slug")

    USERNAME_FIELD = "username"

    def __str__(self):
        return f"[{self.username}]: {self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Uporabniki"
        verbose_name = "Uporabnik"


class Projekt:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Projekti"
        verbose_name = "Projekt"


class Naloga:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Naloge"
        verbose_name = "Naloga"


class Sprint:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sprinti"
        verbose_name = "Sprint"


class Zahteva:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zahteve"
        verbose_name = "Zahteve"


class Ocena:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Ocene"
        verbose_name = "Ocena"


class Zgodba:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zgodbe"
        verbose_name = "Zgodba"


class Komentar:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Komentarji"
        verbose_name = "Komentar"


class Zid:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Zidovi"
        verbose_name = "Zid"


class Opomba:

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Opombe"
        verbose_name = "Opomba"


class Besedila(models.Model):
    tekst = RichTextField(verbose_name="Vsebina besedila")
    naslov = models.CharField(max_length=50, verbose_name="Naslov besedila")
    slug = AutoSlugField(max_length=255, populate_from='naslov', default="", verbose_name="Slug Besedila")

    class Meta:
        verbose_name_plural = "Besedila"

    def __str__(self):
        return f'{self.naslov}'