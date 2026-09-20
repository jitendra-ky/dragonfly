import random
import string

from django.contrib.auth import get_user_model
from django.db import transaction

from zserver.models import SignUpOTP, UnverifiedUser, VerifyUserOTP

User = get_user_model()


class VerificationRepository:
    def create_unverified_user(self, *, email: str, contact: str, password: str) -> UnverifiedUser:
        """Replace a pending signup and create its verification OTP."""
        UnverifiedUser.objects.filter(email=email).delete()
        user = UnverifiedUser.objects.create(
            email=email,
            contact=contact,
            password=password,
        )
        VerifyUserOTP.objects.create(user=user, otp=self._generate_otp())
        return user

    def get_unverified_user(self, email: str) -> UnverifiedUser:
        """Return a pending signup by email."""
        return UnverifiedUser.objects.get(email=email)

    def get_verification_otp(self, user: UnverifiedUser) -> VerifyUserOTP:
        """Return the OTP associated with a pending signup."""
        return VerifyUserOTP.objects.get(user=user)

    @transaction.atomic
    def complete_signup(self, user: UnverifiedUser, otp: VerifyUserOTP) -> User:
        """Create the active user and remove its pending signup records."""
        verified_user = User.objects.create(
            contact=user.contact,
            email=user.email,
            password=user.password,
            is_active=True,
            email_verified=True,
        )
        user.delete()
        otp.delete()
        return verified_user

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
