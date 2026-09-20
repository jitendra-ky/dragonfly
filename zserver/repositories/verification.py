import random
import string

from django.contrib.auth import get_user_model
from django.db import transaction

from zserver.models import SignUpOTP, VerifyUserOTP

User = get_user_model()


class VerificationRepository:
    def create_unverified_user(self, *, email: str, contact: str, password: str) -> User:
        """Replace a pending signup and create its verification OTP."""
        User.objects.filter(username=email, is_active=False).delete()
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=contact,
            password=password,
            is_active=False,
        )
        VerifyUserOTP.objects.create(user=user, otp=self._generate_otp())
        return user

    def get_unverified_user(self, email: str) -> User:
        """Return a pending signup by email."""
        return User.objects.get(username=email, is_active=False)

    def get_verification_otp(self, user: User) -> VerifyUserOTP:
        """Return the OTP associated with a pending signup."""
        return VerifyUserOTP.objects.get(user=user)

    @transaction.atomic
    def complete_signup(self, user: User, otp: VerifyUserOTP) -> User:
        """Activate the built-in user and remove its pending signup records."""
        user.is_active = True
        user.save(update_fields=["is_active"])
        otp.delete()
        return user

    def create_password_reset_otp(self, user: User) -> SignUpOTP:
        """Create a password-reset OTP for a registered user."""
        SignUpOTP.objects.filter(user=user).delete()
        return SignUpOTP.objects.create(user=user, otp=self._generate_otp())

    def get_password_reset_otp(self, user: User) -> SignUpOTP:
        """Return the password-reset OTP for a registered user."""
        return SignUpOTP.objects.get(user=user)

    @staticmethod
    def _generate_otp() -> str:
        return "".join(random.choices(string.digits, k=6))
