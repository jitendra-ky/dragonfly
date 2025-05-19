import random
import string

from django.db import models


# Base model for user profiles
class BaseUserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False, unique=True)
    password = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        abstract = True # don't create a table for this model

    def __str__(self) -> str:
        """Return the email of the user."""
        return self.email

    def is_password_valid(self, password: str) -> bool:
        """Check if the provided password is valid."""
        return self.password == password


# Model for verified user profiles
class UserProfile(BaseUserProfile):
    is_active = models.BooleanField(default=False, blank=False, null=False)

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP for the user."""
        generated_opt = "".join(random.choices(string.digits, k=6))
        otp = SignUpOTP(user=self, otp=generated_opt)
        otp.save()
        return generated_opt


# Model for unverified user profiles
class UnverifiedUserProfile(BaseUserProfile):
    email = models.EmailField(max_length=100, blank=False, null=False, unique=False)


# let's create a signup otp model
class SignUpOTP(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self) -> str:
        """Return the email of the user associated with the OTP."""
        return self.user.email


# let's create a modle for login sessions
class Session(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self) -> str:
        """Return the email of the user associated with the session."""
        return self.user.email

    def is_password_valid(self, password: str) -> bool:
        """Check if the provided password is valid."""
        return self.user.is_password_valid(password)

    def generate_session_id(self) -> str:
        """Generate a unique session ID for the session."""
        generated_session_id = "".join(
            random.choices(string.ascii_letters + string.digits, k=100),
        )
        self.session_id = generated_session_id
        self.save()
        return generated_session_id
