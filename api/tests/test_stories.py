from django.test import TestCase, Client, RequestFactory

from api.stories import StoriesApi

from website.forms import ZgodbaForm
from website.models import Zgodba, Projekt, Uporabnik, ProjectOwner


class StoriesApiTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.project = Projekt.objects.create(ime="Test projekt", opis="Testni opis")
        self.user = Uporabnik.objects.create(
            username="jnovak", first_name="Janez", last_name="Novak",
            email="janez.novak@test.com",
            otp_auth=False)
        self.user.set_password("preprostogeslo")
        self.user.save()
        ProjectOwner.objects.create(projekt=self.project, uporabnik=self.user).save()
        self.zgodba = Zgodba.objects.create(projekt=self.project, ime="Test zgodba",
                              vsebina="Vsebina zgodbe", sprejemni_testi="Sprejemni testi",
                              poslovna_vrednost=4, prioriteta=Zgodba.SHOULD_HAVE)
        self.wrong_user = Uporabnik.objects.create(username="fail", first_name="Failed",
            last_name="User", email="fail@mail.com", otp_auth=False, password="dolgogeslo123")

    def test_story_create_correct(self):
        data = dict(
            ime="Zgodba 1", vsebina="Vsebina zgodbe", sprejemni_testi="Sprejemni testi",
            poslovna_vrednost=4, prioriteta=Zgodba.SHOULD_HAVE
        )
        request = self.factory.post(f'/api/projects/{self.project.id}/stories/', data)
        request.user = self.user
        response = StoriesApi.as_view()(request, self.project.id)
        self.assertEqual(response.status_code, 201, msg="Kreacija zgodbe ni uspela!")

    def test_story_create_fail1(self):
        data = dict(
            ime="Zgodba 1", vsebina="Vsebina zgodbe", sprejemni_testi="Sprejemni testi",
            poslovna_vrednost=15, prioriteta=Zgodba.SHOULD_HAVE
        )
        request = self.factory.post(f'/api/projects/{self.project.id}/stories/', data)
        request.user = self.user
        response = StoriesApi.as_view()(request, self.project.id)
        self.assertEqual(response.status_code, 400, msg="Napačna zgodba je usepla!")

    def test_story_create_fail2(self):
        data = dict(
            ime="Zgodba 1", vsebina="Vsebina zgodbe", sprejemni_testi="Sprejemni testi",
            poslovna_vrednost=3, prioriteta=10
        )
        form = ZgodbaForm(data=data)
        request = self.factory.post(f'/api/projects/{self.project.id}/stories/', data)
        request.user = self.user
        response = StoriesApi.as_view()(request, self.project.id)
        self.assertEqual(response.status_code, 400, msg="Napačna zgodba je usepla!")

    def test_story_create_fail_duplicate(self):
        data = dict(ime = "Test zgodba", vsebina = "Vsebina zgodbe", sprejemni_testi = "Sprejemni testi",
            poslovna_vrednost = 4, prioriteta = Zgodba.SHOULD_HAVE
        )
        request = self.factory.post(f'/api/projects/{self.project.id}/stories/', data)
        request.user = self.user
        response = StoriesApi.as_view()(request, self.project.id)
        self.assertEqual(response.status_code, 400, msg="Zgodba s podvojenim imenom je bila ustvarjena!")

    def test_story_delete(self):
        request = self.factory.delete(f'/api/projects/{self.project.id}/stories/{self.zgodba.id}/')
        request.user = self.user
        response = StoriesApi.as_view()(request, self.project.id, self.zgodba.id)
        self.assertEqual(response.status_code, 204, msg="Brisanje zgodbe ni uspelo!")

    def test_wrong_credentials_get(self):
        request = self.factory.get(f'/api/projects/{self.project.id}/stories/')
        request.user = self.wrong_user
        response = StoriesApi.as_view()(request, self.project.id)
        self.assertEqual(response.status_code, 403, msg="Access by unauthorized user for GET!")

    def test_wrong_credentials_post(self):
        request = self.factory.post(f'/api/projects/{self.project.id}/stories/', data={})
        request.user = self.wrong_user
        response = StoriesApi.as_view()(request, self.project.id)
        self.assertEqual(response.status_code, 403, msg="Access by unauthorized user for POST!")

    def test_wrong_credentials_delete(self):
        request = self.factory.delete(f'/api/projects/{self.project.id}/stories/{self.zgodba.id}')
        request.user = self.wrong_user
        response = StoriesApi.as_view()(request, self.project.id, self.zgodba.id)
        self.assertEqual(response.status_code, 403, msg="Access by unauthorized user for DELETE!")

    def test_update(self):
        data = dict(
            ime="Zgodba 5", vsebina="Vsebina zgodbe", sprejemni_testi="Sprejemni testi",
            poslovna_vrednost=3, prioriteta=Zgodba.SHOULD_HAVE
        )
        request = self.factory.post(f'/api/projects/{self.project.id}/stories/{self.zgodba.id}/', data=data)
        request.user = self.user
        response = StoriesApi.as_view()(request, self.project.id, self.zgodba.id)
        self.assertEqual(response.status_code, 201, msg="Update failed!")