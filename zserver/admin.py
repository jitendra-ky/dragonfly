from django.contrib import admin

from zserver.models import Message, Session, SignUpOTP, UserProfile, VerifyUserOTP, UnverifiedUserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(SignUpOTP)
admin.site.register(Session)
admin.site.register(VerifyUserOTP)
admin.site.register(UnverifiedUserProfile)

admin.site.register(Message)
