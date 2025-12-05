from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q  # Import Q object for building complex queries using OR conditions
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from zserver.models import (
    Message,
    SignUpOTP,
    UnverifiedUser,
    VerifyUserOTP,
)

User = get_user_model()


# Serializer class for the User model
class UserProfileSerializer(serializers.ModelSerializer):
    # Add dynamic field for last message between the user and the contact
    last_message = serializers.SerializerMethodField()

    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = User  # Specify the model to be serialized
        fields = [
            "id",
            "contact",
            "email",
            "password",
            "last_message",
        ]  # Fields to be included in the serialization
        extra_kwargs = {
            "password": {"write_only": True},  # Make the password field write-only
        }

    def get_last_message(self, contact: User) -> str:
        """Retrieve the last message exchanged with the given contact."""
        # Get the authenticated user from serializer context
        user = self.context.get("user")
        if not user:
            return None

        # Fetch the latest message between user and this contact
        last_msg = Message.objects.filter(
            Q(sender=user, receiver=contact) | Q(sender=contact, receiver=user),
        ).order_by("-timestamp").first()

        # Return message text if available, else None
        return last_msg.content if last_msg else None

    def update(self, instance: User, validated_data: dict) -> User:
        """Update an existing user profile."""
        instance.contact = validated_data.get("contact", instance.contact)
        instance.email = validated_data.get("email", instance.email)
        
        # Use set_password for proper hashing
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        
        instance.save()
        return instance


# Serializer class for the UnverifiedUser model
class UnverifiedUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = UnverifiedUser
        fields = [
            "contact",
            "email",
            "password",
        ]  # Fields to be included in the serialization
        extra_kwargs = {
            "password": {"write_only": True},  # Make the password field write-only
        }

    def validate_email(self, value: str) -> str:
        """Validate that the email is not already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def create(self, validated_data: dict) -> UnverifiedUser:
        """Create a new unverified user profile."""
        if UnverifiedUser.objects.filter(email=validated_data["email"]).exists():
            UnverifiedUser.objects.filter(email=validated_data["email"]).delete()
        # Create a new unverified user profile
        # and generate an OTP for verification
        # Hash the password before storing
        from django.contrib.auth.hashers import make_password
        validated_data["password"] = make_password(validated_data["password"])
        user = UnverifiedUser.objects.create(**validated_data)
        user.generate_otp()
        return user


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
            user = UnverifiedUser.objects.get(email=email)
        except UnverifiedUser.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        try:
            user_otp = VerifyUserOTP.objects.get(user=user)
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
        user = User(
            contact=unverified_user.contact,
            email=unverified_user.email,
            password=unverified_user.password,  # Already hashed
            is_active=True,
            email_verified=True,
        )
        user.save()
        unverified_user.delete()
        self.validated_data["user_otp"].delete()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "contact": user.contact,
            }
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
            user = User.objects.get(email=email)
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
                "contact": user.contact,
            }
        }


class ForgotPasswordSerializer(serializers.Serializer):
    """responsible for sending the OTP to the user's email for password reset."""

    email = serializers.EmailField(max_length=100)

    def validate_email(self, value: str) -> str:
        """Validate that the email exists in the database."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def send_reset_otp(self) -> None:
        """Send a password reset OTP to the user."""
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        user.generate_otp()
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
            user = User.objects.get(email=email)
        except User.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        try:
            user_otp = SignUpOTP.objects.get(user=user)
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
