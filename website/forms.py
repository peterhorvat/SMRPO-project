from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Uporabnik, Projekt, Zgodba
from django.forms import ModelForm
from django.core.exceptions import ValidationError


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


class OTPForm(forms.Form):
    otp_code = forms.CharField(max_length=10, label="OTP koda", help_text="Vnesite OTP kodo iz avtentikatorja", widget=forms.TextInput(attrs={'autocomplete': 'off', 'autofocus': ''}))


class NewZgodbaForm(ModelForm):
    def clean_ime(self):
        ime = self.cleaned_data['ime']
        if len(Zgodba.objects.filter(ime=ime)) > 0 and Zgodba.objects.filter(ime=ime) is not self:
            raise ValidationError("Zgodba s tem imenom že obstaja")
        return ime

    class Meta:
        model = Zgodba
        fields = ['ime', 'vsebina', 'sprejemni_testi', 'poslovna_vrednost', 'prioriteta']
        help_texts = {'poslovna_vrednost': 'Vnesite število med 0 in 10.'}
