from django.contrib.auth.forms import AuthenticationForm
from .models import Uporabnik, Projekt
from django.forms import ModelForm


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = Uporabnik
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Uporabniško ime"
        self.fields['password'].label = "Geslo"


class CreateNewProjectForm(ModelForm):
    class Meta:
        model = Projekt
        fields = ['ime']

    def __init__(self, *args, **kwargs):
        super(CreateNewProjectForm, self).__init__(*args, **kwargs)
        self.fields['ime'].label = "Ime projekta"