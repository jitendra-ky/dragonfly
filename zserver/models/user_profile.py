import random
import string

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: bool) -> "User":
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(
            self, email: str, password: str | None = None, **extra_fields: bool) -> "User":
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model using email as the unique identifier."""

    email = models.EmailField(max_length=100, unique=True, blank=False, null=False)
    contact = models.CharField(max_length=100, blank=False, null=False)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["contact"]

    class Meta:
        """Meta options for User model."""

        db_table = "zserver_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        """Return the email of the user."""
        return self.email

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP for the user."""
        generated_otp = "".join(random.choices(string.digits, k=6))
        otp = SignUpOTP(user=self, otp=generated_otp)
        otp.save()
        return generated_otp


class UnverifiedUser(models.Model):
    """Temporary storage for users pending email verification."""

    email = models.EmailField(max_length=100, blank=False, null=False)
    contact = models.CharField(max_length=100, blank=False, null=False)
    password = models.CharField(max_length=128, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for UnverifiedUser model."""

        db_table = "zserver_unverifieduser"

    def __str__(self) -> str:
        """Return the email of the unverified user."""
        return self.email

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP for the unverified user."""
        generated_otp = "".join(random.choices(string.digits, k=6))
        otp = VerifyUserOTP(user=self, otp=generated_otp)
        otp.save()
        return generated_otp



# let's create a signup otp model
class SignUpOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        """Meta options for SignUpOTP model."""

        db_table = "zserver_signupotp"

    def __str__(self) -> str:
        """Return the email of the user associated with the OTP."""
        return self.user.email


# let's create a VerifyUserOTP model
class VerifyUserOTP(models.Model):
    user = models.ForeignKey(UnverifiedUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        """Meta options for VerifyUserOTP model."""

        db_table = "zserver_verifyuserotp"

    def __str__(self) -> str:
        """Return the email of the user associated with the OTP."""
        return self.user.email + " " + self.otp
