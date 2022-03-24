from django.test import TestCase, Client
from django.contrib.auth import authenticate

from website.models import Uporabnik

class UporabnikTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Uporabnik.objects.create(
            username="jnovak", first_name="Janez", last_name="Novak",
            email="janez.novak@test.com",
            otp_auth=False)
        jnovak = Uporabnik.objects.get(username="jnovak")
        jnovak.set_password("preprostogeslo")
        jnovak.save()

        Uporabnik.objects.create(
            username="anovak", first_name="Anton", last_name="Novak",
            email="anton.novak@test.com",
            otp_auth=False)
        anovak = Uporabnik.objects.get(username="anovak")
        anovak.set_password('   cudn  ogeslo    ')
        anovak.save()


    def test_correct_data(self):
        c = Client()
        success = c.login(username='jnovak', password='preprostogeslo')
        self.assertTrue(success, "Prijava s pravilnimi podatki ni upsela!")

    def test_wrong_password(self):
        c = Client()
        success = c.login(username='jnovak', password='napacnogeslo123')
        self.assertFalse(success, "Prijava z napačnim geslom je uspela!")

    def test_wrong_username(self):
        c = Client()
        success = c.login(username='napacni-uporabnik', password='preprostogeslo')
        self.assertFalse(success, "Prijava z napačnim uporabnikom je uspela!")

    def test_passowrd(self):
        c = Client()
        success = c.login(username='anovak', password='   cudn  ogeslo    ')
        self.assertTrue(success, "Prijava z geslom s presledki ni uspela!")
