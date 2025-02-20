import random
import string

from django.db import models


# the UserProfile is the model that will be used to store the user's profile information
class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False, unique=True)
    password = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)
    is_active = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self) -> str:
        return self.email

    def generate_otp(self) -> str:
        generated_opt = "".join(random.choices(string.digits, k=6))
        OTP = SignUpOTP(user=self, otp=generated_opt)
        OTP.save()
        return generated_opt

    def is_password_valid(self, password: str) -> bool:
        return self.password == password


# let's create a signup otp model
class SignUpOTP(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self) -> str:
        return self.user.email


# let's create a modle for login sessions
class Session(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self) -> str:
        return self.user.email

    def is_password_valid(self, password: str) -> bool:
        return self.user.is_password_valid(password)

    def generate_session_id(self) -> str:
        generated_session_id = "".join(
            random.choices(string.ascii_letters + string.digits, k=100),
        )
        self.session_id = generated_session_id
        self.save()
        return generated_session_id
