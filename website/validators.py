from django.core.exceptions import ValidationError


class CustomPasswordValidator:

    def validate(self, password, user=None):
        with open('pass_dict.txt') as myfile:
            if password in myfile.read():
                raise ValidationError(f"Geslo ne sme biti eno izmed pogosto uporabljenih gesel")

    def get_help_text(self):
        return "Geslo ne sme biti eno izmed pogosto uporabljenih gesel"


class MaxLengthPasswordValidator:
    def validate(self, password, user=None):
        if len(password) > 128:
            raise ValidationError("Geslo ne sme biti daljše od 128 znakov")

    def get_help_text(self):
        return "Geslo ne sme biti daljše od 128 znakov"

