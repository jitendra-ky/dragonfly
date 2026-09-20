from django.conf import settings
from django.db import models


class SignUpOTP(models.Model):
    """One-time password for signup verification and password resets."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        """Meta options for SignUpOTP model."""

        db_table = "zserver_signupotp"

    def __str__(self) -> str:
        """Return the email of the user associated with the OTP."""
        return self.user.email


class VerifyUserOTP(models.Model):
    """One-time password for verifying an inactive built-in Django user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        """Meta options for VerifyUserOTP model."""

        db_table = "zserver_verifyuserotp"

    def __str__(self) -> str:
        """Return the email and OTP."""
        return self.user.email + " " + self.otp
