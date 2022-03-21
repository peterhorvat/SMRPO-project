from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Uporabnik


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = Uporabnik
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Uporabniško ime"
        self.fields['password'].label = "Geslo"


class OTPForm(forms.Form):
    otp_code = forms.CharField(max_length=10, label="OTP koda", help_text="Vnesite OTP kodo iz avtentikatorja",
                               widget=forms.TextInput(attrs={'autocomplete': 'off', 'autofocus': ''}))