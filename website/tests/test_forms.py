from django.test import TestCase

from website.forms import NewZgodbaForm
from website.models import Zgodba, Projekt


class ZgodbaFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Projekt.objects.create(ime="Test projekt").save()
        projekt = Projekt.objects.get(ime="Test projekt")
        Zgodba.objects.create(projekt=projekt, ime = "Test zgodba", vsebina = "Vsebina zgodbe", sprejemni_testi = "Sprejemni testi",
            poslovna_vrednost = 4, prioriteta = Zgodba.SHOULD_HAVE).save()

    def test_correct_zgodba(self):
        data = dict(
            ime = "Zgodba 1", vsebina = "Vsebina zgodbe", sprejemni_testi = "Sprejemni testi",
            poslovna_vrednost = 4, prioriteta = Zgodba.SHOULD_HAVE
        )
        form = NewZgodbaForm(data=data)
        self.assertTrue(form.is_valid(), "Pravilna zgodba ni usepla!")

    def test_wrong_zgodba1(self):
        data = dict(
            ime = "Zgodba 1", vsebina = "Vsebina zgodbe", sprejemni_testi = "Sprejemni testi",
            poslovna_vrednost = 15, prioriteta = Zgodba.SHOULD_HAVE
        )
        form = NewZgodbaForm(data=data)
        self.assertFalse(form.is_valid(), "Napačna zgodba je usepla!")

    def test_wrong_zgodba2(self):
        data = dict(
            ime = "Zgodba 1", vsebina = "Vsebina zgodbe", sprejemni_testi = "Sprejemni testi",
            poslovna_vrednost = 3, prioriteta = 10
        )
        form = NewZgodbaForm(data=data)
        self.assertFalse(form.is_valid(), "Napačna zgodba je usepla!")

    def test_duplicate_zgodba(self):
        data = dict(ime = "Test zgodba", vsebina = "Vsebina zgodbe", sprejemni_testi = "Sprejemni testi",
            poslovna_vrednost = 4, prioriteta = Zgodba.SHOULD_HAVE
        )
        form = NewZgodbaForm(data=data)
        self.assertFalse(form.is_valid(), "Zgodba s podvojenim imenom je bila ustvarjena!")