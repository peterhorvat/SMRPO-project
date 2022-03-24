from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
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


class UporabnikCreationForm(UserCreationForm):
    class Meta:
        model = Uporabnik
        fields = ['username', 'first_name', 'last_name', 'email']


class UporabnikChangeForm(UserChangeForm):
    class Meta:
        model = Uporabnik
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username' : 'Uporabniško ime',
            'first_name': 'Ime',
            'last_name': 'Priimek',
        }

    def __init__(self, *args, **kwargs):
        super(UporabnikChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = "Geslo"
        self.fields['password'].help_text = ""

class CreateNewProjectForm(ModelForm):
    class Meta:
        model = Projekt
        fields = ['ime']

    def __init__(self, *args, **kwargs):
        super(CreateNewProjectForm, self).__init__(*args, **kwargs)
        self.fields['ime'].label = "Ime projekta"


class OTPForm(forms.Form):
    otp_code = forms.CharField(max_length=10, label="OTP koda", help_text="Vnesite OTP kodo iz avtentikatorja",
                               widget=forms.TextInput(attrs={'autocomplete': 'off', 'autofocus': ''}))


class NewZgodbaForm(ModelForm):
    def clean_ime(self):
        ime = self.cleaned_data['ime']
        if len(Zgodba.objects.filter(ime=ime)) > 0:
            raise ValidationError("Zgodba s tem imenom že obstaja")
        return ime

    class Meta:
        model = Zgodba
        fields = ['ime', 'vsebina', 'sprejemni_testi', 'poslovna_vrednost', 'prioriteta']
        help_texts = {'poslovna_vrednost': 'Vnesite število med 0 in 10.'}
        widgets = {
            'poslovna_vrednost': forms.NumberInput(attrs={'min': 0, 'max': 10})
        }


class NewUporabnikForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(ModelForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['password'].required = False

    def clean_username(self):
        ime = self.cleaned_data['username']
        if len(Zgodba.objects.filter(ime=ime)) > 0:
            raise ValidationError("Uporanik s tem uporabniskim imenom že obstaja")
        return ime

    class Meta:
        model = Uporabnik
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'otp_auth']
        #help_texts = {'poslovna_vrednost': 'Vnesite število med 0 in 10.'}
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }
