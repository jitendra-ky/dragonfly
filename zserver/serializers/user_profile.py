from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from zserver.domain.entities import User as UserEntity
from zserver.models import SignUpOTP, VerifyUserOTP
from zserver.repositories import MessageRepository, UserRepository, VerificationRepository

User = get_user_model()


# Serializer class for the User model
class UserProfileSerializer(serializers.Serializer):
    # Add dynamic field for last message between the user and the contact
    last_message = serializers.SerializerMethodField()
    id = serializers.IntegerField(read_only=True)
    contact = serializers.CharField(source="first_name")
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False)

    def get_last_message(self, contact: User | UserEntity) -> str | None:
        """Retrieve the last message exchanged with the given contact."""
        # Get the authenticated user from serializer context
        user = self.context.get("user")
        if not user:
            return None

        messages = MessageRepository().conversation(
            user_id=user.id,
            contact_id=contact.id,
        )
        return messages[-1].content if messages else None

    def update(self, instance: User, validated_data: dict) -> User:
        """Update an existing user profile."""
        return UserRepository().update(
            instance,
            contact=validated_data.get("first_name", instance.first_name),
            email=validated_data.get("email", instance.email),
            password=validated_data.get("password"),
        )


# Serializer class for the UnverifiedUser model
class UnverifiedUserProfileSerializer(serializers.Serializer):
    contact = serializers.CharField(source="first_name")
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        """Meta class to specify the model and fields to be serialized."""

    def validate_email(self, value: str) -> str:
        """Validate that the email is not already in use."""
        if UserRepository().email_exists(value):
            raise serializers.ValidationError("Email is already in use.")
        return value

    def create(self, validated_data: dict) -> User:
        """Create a new unverified user profile."""
        return VerificationRepository().create_unverified_user(
            contact=validated_data["first_name"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


# serializer for VerifyUserOTP model
class VerifyUserOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)

    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = VerifyUserOTP
        fields = ["otp", "email"]

    def validate(self, data: dict) -> dict:
        """Validate the OTP and email."""
        email = data.get("email")
        otp = data.get("otp")

        try:
            user = VerificationRepository().get_unverified_user(email)
        except User.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        try:
            user_otp = VerificationRepository().get_verification_otp(user)
        except VerifyUserOTP.DoesNotExist as err:
            raise serializers.ValidationError({"otp": "OTP does not exist."}) from err

        if user_otp.otp != otp:
            raise serializers.ValidationError({"otp": "Incorrect OTP."})

        data["user"] = user
        data["user_otp"] = user_otp
        return data

    def signup_user(self) -> dict:
        """Add user to User table, delete the OTP, and return JWT tokens."""
        unverified_user = self.validated_data["user"]
        # Create verified user with already-hashed password
        user = VerificationRepository().complete_signup(
            unverified_user,
            self.validated_data["user_otp"],
        )

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "contact": user.first_name,
            },
        }


class LoginSerializer(serializers.Serializer):
    """Serializer for user login that returns JWT tokens."""

    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        """Validate the email and password."""
        email = data.get("email")
        password = data.get("password")

        # First check if user exists
        try:
            user = UserRepository().get_by_email(email)
        except User.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        # Check password manually (works for both active and inactive users)
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError({"user": "User is not active."})

        data["user"] = user
        return data

    def get_tokens(self) -> dict:
        """Generate and return JWT tokens for the user."""
        user = self.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "contact": user.first_name,
            },
        }


class ForgotPasswordSerializer(serializers.Serializer):
    """responsible for sending the OTP to the user's email for password reset."""

    email = serializers.EmailField(max_length=100)

    def validate_email(self, value: str) -> str:
        """Validate that the email exists in the database."""
        if not UserRepository().email_exists(value):
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def send_reset_otp(self) -> None:
        """Send a password reset OTP to the user."""
        email = self.validated_data["email"]
        user = UserRepository().get_by_email(email)
        VerificationRepository().create_password_reset_otp(user)
        print(f"Sending password reset OTP to {email}")


class ResetPasswordSerializer(serializers.Serializer):
    """responsible for resetting the user's password."""

    email = serializers.EmailField(max_length=100)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        """Validate the OTP and email."""
        email = data.get("email")
        otp = data.get("otp")

        try:
            user = UserRepository().get_by_email(email)
        except User.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        try:
            user_otp = VerificationRepository().get_password_reset_otp(user)
        except SignUpOTP.DoesNotExist as err:
            raise serializers.ValidationError({"otp": "OTP does not exist."}) from err

        if user_otp.otp != otp:
            raise serializers.ValidationError({"otp": "Incorrect OTP."})

        data["user"] = user
        data["user_otp"] = user_otp
        return data

    def reset_password(self) -> None:
        """Reset the user's password using set_password for proper hashing."""
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        self.validated_data["user_otp"].delete()
