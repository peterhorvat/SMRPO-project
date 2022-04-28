from datetime import datetime, date

import pytz
from django import forms

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.db.models import Sum

from .models import Uporabnik, Projekt, Zgodba, Sprint, Naloga, Clan, Objava

from django.forms import ModelForm, DateInput
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


class SprintForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self._pid = kwargs.pop('pid', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Sprint
        fields = ['ime', 'zacetni_cas', 'koncni_cas', 'hitrost']
        help_texts = {'hitrost': 'Vnesite pozitivno celo število.'}
        widgets = {
            'hitrost': forms.NumberInput(attrs={'min': 1, 'type': 'number'}),
            'zacetni_cas': forms.DateInput(
                format='%d.%m.%Y',
                attrs={'placeholder': 'Izberite datum',
                       'type': 'date'
                       }),
            'koncni_cas': forms.DateInput(
                format='%d.%m.%Y',
                attrs={'placeholder': 'Izberite datum',
                       'type': 'date'
                       }),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        zacetni_cas = cleaned_data.get("zacetni_cas")
        koncni_cas = cleaned_data.get("koncni_cas")
        projekt = Projekt.objects.get(id=self._pid)
        if Sprint.objects.filter(projekt=projekt, zacetni_cas__lt=koncni_cas, koncni_cas__gt=zacetni_cas).exists():
            raise forms.ValidationError("Sprint v tem obdobju že obstaja.")
        if zacetni_cas > koncni_cas:
            raise forms.ValidationError("Končni čas ne sme biti pred začetnim časom!")
        if zacetni_cas < date.today():
            raise forms.ValidationError("Začetni čas ne sme biti v preteklosti!")
        return cleaned_data


class EditSprintFormTekoci(ModelForm):
    class Meta:
        model = Sprint
        fields = ['hitrost']
        help_texts = {'hitrost': 'Vnesite pozitivno celo število.'}
        widgets = {
            'hitrost': forms.NumberInput(attrs={'min': 1, 'type': 'number'}),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        hitrost = cleaned_data.get("hitrost")
        sum_tock = Zgodba.objects.filter(sprint_id=self.instance.id).aggregate(sum=Sum('ocena'))['sum']
        if int(hitrost) < int(sum_tock):
            raise forms.ValidationError("Hitrost ne sme biti nižja od skupnega števila točk zgodb!")
        return cleaned_data


class EditSprintForm(ModelForm):
    projekt = forms.ModelChoiceField(queryset=Projekt.objects.all(), disabled=True)

    class Meta:
        model = Sprint
        fields = ['projekt', 'ime', 'hitrost', 'zacetni_cas', 'koncni_cas']
        help_texts = {'hitrost': 'Vnesite pozitivno celo število.'}
        widgets = {
            'hitrost': forms.NumberInput(attrs={'min': 1, 'type': 'number'}),
            'zacetni_cas': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'placeholder': 'Izberite datum',
                       'type': 'date'
                       }),
            'koncni_cas': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'placeholder': 'Izberite datum',
                       'type': 'date'
                       }),
        }

    def clean(self):
        cleaned_data = self.cleaned_data  # individual field's clean methods have already been called
        zacetni_cas = cleaned_data.get("zacetni_cas")
        koncni_cas = cleaned_data.get("koncni_cas")
        projekt = cleaned_data.get("projekt")
        hitrost = cleaned_data.get("hitrost")
        sum_tock = Zgodba.objects.filter(sprint_id=self.instance.id).aggregate(sum=Sum('ocena'))['sum']
        if int(hitrost) < int(sum_tock):
            raise forms.ValidationError("Hitrost ne sme biti nižja od skupnega števila točk zgodb!")
        if ("zacetni_cas" in self.changed_data or "koncni_cas" in self.changed_data) and \
                Sprint.objects.filter(projekt=projekt, zacetni_cas__lt=koncni_cas, koncni_cas__gt=zacetni_cas).exclude(
                    id=self.instance.id).exists():
            raise forms.ValidationError("Sprint v tem obdobju že obstaja.")
        if zacetni_cas > koncni_cas:
            raise forms.ValidationError("Končni čas ne sme biti pred začetnim časom!")
        if zacetni_cas < date.today():
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


class NalogaForm(forms.ModelForm):
    class Meta:
        model = Naloga
        fields = ['ime', 'opis', 'cas', 'clan']
        widgets = {
            'cas': forms.NumberInput(attrs={'min': 0, 'type': 'number'})
        }

    def __init__(self, *args, **kwargs):
        projekt_id = kwargs.pop('projekt_id', None)
        super(NalogaForm, self).__init__(*args, **kwargs)
        self.fields['clan'].queryset = Clan.objects.filter(projekt_id=projekt_id)


class ZgodbaOpombeForm(forms.ModelForm):
    class Meta:
        model = Zgodba
        fields = ['opombe']


class ObjavaForm(forms.ModelForm):
    class Meta:
        model = Objava
        fields = ['naslov', 'vsebina']
