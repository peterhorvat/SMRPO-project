import base64
import qrcode
from io import BytesIO
from django_otp.plugins.otp_totp.models import TOTPDevice

def BaseOTP(request):

    if request.user.is_authenticated:
        if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
            title = "OTP je vklopljen"
            text = "<small> V primeru, da ste izgubili OTP avtentikator nam to sporočite</small>"
            button1 = "Ponastavi"
            button2 = "Izklopi"
            icon = "success"
            activated = True
        else:
            if TOTPDevice.objects.filter(user=request.user, confirmed=False).exists():
                device = TOTPDevice.objects.get(user=request.user)
                device.delete()
            device = TOTPDevice(user=request.user, name=f"SMRPO {request.user.username}", confirmed=False)
            device.save()
            qr = qrcode.make(device.config_url)
            img = qr.get_image()
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            text = f"<img width='70%' src='data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}' alt='QR CODE'/>"
            title = "OTP avtentikacija"
            button1 = "Vklopi OTP"
            button2 = ""
            icon = ""
            activated = False
        return {
            'icon': icon,
            'title': title,
            'button1': button1,
            'button2': button2,
            'activated': activated,
            'text': text
        }
    else:
        return {
            'otp_message': 'message',
            'icon': 'icon',
            'title': 'title',
            'activated': True
        }