from django.contrib import admin

from zserver.models import (
    Message,
    SignUpOTP,
    VerifyUserOTP,
)

# Register your models here.
admin.site.register(SignUpOTP)
admin.site.register(VerifyUserOTP)
admin.site.register(Message)
