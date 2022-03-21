import re

from django.http import HttpResponseRedirect
from django.urls import reverse


class LoginOTPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            if not request.user.otp_auth:
                if not re.match("|".join([r"/loginOTP/?",
                                          r"/createOTP/?"]), request.path):
                    return HttpResponseRedirect(reverse("loginOTP"))

        return response