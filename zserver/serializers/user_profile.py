from rest_framework import serializers

from zserver.models import Session, SignUpOTP, UserProfile, UnverifiedUserProfile


# Serializer class for the UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = UserProfile  # Specify the model to be serialized
        fields = [
            "id",
            "fullname",
            "email",
            "password",
        ]  # Fields to be included in the serialization
        extra_kwargs = {
            "password": {"write_only": True},  # Make the password field write-only
        }

    def create(self, validated_data: dict) -> UserProfile:
        """Create a new user profile and generate OTP."""
        user = UserProfile.objects.create(**validated_data)
        return user

    def update(self, instance: UserProfile, validated_data: dict) -> UserProfile:
        """Update an existing user profile."""
        instance.fullname = validated_data.get("fullname", instance.fullname)
        instance.email = validated_data.get("email", instance.email)
        instance.password = validated_data.get("password", instance.password)
        instance.save()
        return instance


# Serializer class for the UnverifiedUserProfile model
class UnverifiedUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = UnverifiedUserProfile
        fields = [
            "fullname",
            "email",
            "password",
        ]  # Fields to be included in the serialization
        extra_kwargs = {
            "password": {"write_only": True},  # Make the password field write-only
        }
    
    def validate_email(self, value: str) -> str:
        """Validate that the email is not already in use."""
        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def create(self, validated_data: dict) -> UnverifiedUserProfile:
        """Create a new unverified user profile."""
        if UnverifiedUserProfile.objects.filter(email=validated_data["email"]).exists():
            UnverifiedUserProfile.objects.filter(email=validated_data["email"]).delete()
        # Create a new unverified user profile
        # and generate an OTP for verification
        user = UnverifiedUserProfile.objects.create(**validated_data)
        user.generate_otp()
        return user


# Serializer class for the SignUpOTP model
class SignUpOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)

    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = SignUpOTP
        fields = ["otp", "email"]

    def validate(self, data: dict) -> dict:
        """Validate the OTP and email."""
        email = data.get("email")
        otp = data.get("otp")

        try:
            user = UnverifiedUserProfile.objects.get(email=email)
        except UnverifiedUserProfile.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        try:
            user_otp = SignUpOTP.objects.get(user=user)
        except SignUpOTP.DoesNotExist as err:
            raise serializers.ValidationError({"otp": "OTP does not exist."}) from err

        if user_otp.otp != otp:
            raise serializers.ValidationError({"otp": "Incorrect OTP."})

        return data

    def make_user_verified(self) -> None:
        """Activate the user."""
        unverfied_user = UnverifiedUserProfile.objects.get(email=self.validated_data["email"])
        user = UserProfile(
            fullname=unverfied_user.fullname,
            email=unverfied_user.email,
            password=unverfied_user.password,
            is_active=True,
        )
        user.save()
        unverfied_user.delete() # as user deleted it's otp will be automatically deleted

class SessionSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        """Validate the email and password."""
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist as err:
            raise serializers.ValidationError({"email": "User does not exist."}) from err

        if not user.is_password_valid(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        if not user.is_active:
            raise serializers.ValidationError({"user": "User is not active."})

        data["user"] = user
        return data

    def create(self, validated_data: dict) -> Session:
        """Create a new session for the user."""
        user = validated_data["user"]
        session = Session(user=user)
        session.generate_session_id()
        session.save()
        return session


class ForgotPasswordSerializer(serializers.Serializer):
    """responsible for sending the OTP to the user's email for password reset."""

    email = serializers.EmailField(max_length=100)

    def validate_email(self, value: str) -> str:
        """Validate that the email exists in the database."""
        if not UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def send_reset_otp(self) -> None:
        """Send a password reset OTP to the user."""
        email = self.validated_data["email"]
        user = UserProfile.objects.get(email=email)
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
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist as err:
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
        """Reset the user's password."""
        user = self.validated_data["user"]
        user.password = self.validated_data["new_password"]
        user.save()
        self.validated_data["user_otp"].delete()
