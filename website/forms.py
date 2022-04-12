from datetime import datetime

import pytz
from django import forms

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import Uporabnik, Projekt, Zgodba, Sprint

from django.forms import ModelForm
from django.core.exceptions import ValidationError


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'


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
            'username': 'Uporabniško ime',
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
        fields = ['ime', "opis"]

    def __init__(self, *args, **kwargs):
        super(CreateNewProjectForm, self).__init__(*args, **kwargs)
        self.fields['ime'].label = "Ime projekta"


class OTPForm(forms.Form):
    otp_code = forms.CharField(max_length=10, label="OTP koda", help_text="Vnesite OTP kodo iz avtentikatorja",
                               widget=forms.TextInput(attrs={'autocomplete': 'off', 'autofocus': ''}))


class ZgodbaForm(ModelForm):
    class Meta:
        model = Zgodba
        fields = ['ime', 'vsebina', 'sprejemni_testi', 'poslovna_vrednost', 'prioriteta']
        help_texts = {'poslovna_vrednost': 'Vnesite število med 1 in 10.'}
        widgets = {
            'poslovna_vrednost': forms.NumberInput(attrs={'min': 1, 'max': 10})
        }

#TODO: DATETIME NAMESTO DATE
class SprintForm(ModelForm):
    projekt = forms.ModelChoiceField(queryset=Projekt.objects.all())
    class Meta:
        model = Sprint
        fields = ['ime', 'projekt', 'zacetni_cas', 'koncni_cas', 'hitrost']
        help_texts = {'hitrost': 'Vnesite pozitivno celo število.'}
        widgets = {
            'hitrost': forms.NumberInput(attrs={'min': 1, 'type': 'number'}),
            'zacetni_cas': DateTimeInput(format=""),
            'koncni_cas': DateTimeInput(),
        }

    def clean(self):
        cleaned_data = self.cleaned_data  # individual field's clean methods have already been called
        zacetni_cas = cleaned_data.get("zacetni_cas")
        koncni_cas = cleaned_data.get("koncni_cas")
        projekt = cleaned_data.get("projekt")
        if Sprint.objects.filter(projekt=projekt, zacetni_cas__lt=koncni_cas, koncni_cas__gt=zacetni_cas).exists():
            raise forms.ValidationError("Sprint v tem obdobju že obstaja.")
        if zacetni_cas > koncni_cas:
            raise forms.ValidationError("Končni čas ne sme biti pred začetnim časom!")
        if zacetni_cas.timestamp() < datetime.now(pytz.timezone('Europe/Ljubljana')).timestamp():
            raise forms.ValidationError("Začetni čas ne sme biti v preteklosti!")
        return cleaned_data


class EditSprintForm(ModelForm):

    class Meta:
        model = Sprint
        fields = ['ime', 'hitrost']
        help_texts = {'hitrost': 'Vnesite pozitivno celo število.'}
        widgets = {
            'hitrost': forms.NumberInput(attrs={'min': 1, 'type': 'number'})
        }


class EditSprintFormAdmin(ModelForm):
    projekt = forms.ModelChoiceField(queryset=Projekt.objects.all(), disabled=True)
    class Meta:
        model = Sprint
        fields = ['projekt', 'ime', 'hitrost', 'zacetni_cas', 'koncni_cas']
        help_texts = {'hitrost': 'Vnesite pozitivno celo število.'}
        widgets = {
            'hitrost': forms.NumberInput(attrs={'min': 1, 'type': 'number'}),
            'zacetni_cas': DateTimeInput(),
            'koncni_cas': DateTimeInput(),
        }

    def clean(self):
        cleaned_data = self.cleaned_data  # individual field's clean methods have already been called
        zacetni_cas = cleaned_data.get("zacetni_cas")
        koncni_cas = cleaned_data.get("koncni_cas")
        projekt = cleaned_data.get("projekt")
        if Sprint.objects.filter(projekt=projekt, zacetni_cas__lt=koncni_cas, koncni_cas__gt=zacetni_cas).exists():
            raise forms.ValidationError("Sprint v tem obdobju že obstaja.")
        if zacetni_cas > koncni_cas:
            raise forms.ValidationError("Končni čas ne sme biti pred začetnim časom!")
        if zacetni_cas.timestamp() < datetime.now(pytz.timezone('Europe/Ljubljana')).timestamp():
            raise forms.ValidationError("Začetni čas ne sme biti v preteklosti!")
        return cleaned_data


class NewUporabnikForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(ModelForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['password'].required = False

    def clean_username(self):
        ime = self.cleaned_data['username']
        if Zgodba.objects.filter(ime=ime).count() > 0:
            raise ValidationError("Uporanik s tem uporabniskim imenom že obstaja")
        return ime

    class Meta:
        model = Uporabnik
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'otp_auth']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }
