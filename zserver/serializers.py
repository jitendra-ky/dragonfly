from rest_framework import serializers

from .models import Session, SignUpOTP, UserProfile


# Serializer class for the UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile  # Specify the model to be serialized
        fields = [
            "fullname",
            "email",
            "password",
        ]  # Fields to be included in the serialization
        extra_kwargs = {
            "password": {"write_only": True}  # Make the password field write-only
        }

    def create(self, validated_data):
        user = UserProfile.objects.create(**validated_data)
        user.generate_otp()
        return user

    def update(self, instance, validated_data):
        instance.fullname = validated_data.get("fullname", instance.fullname)
        instance.email = validated_data.get("email", instance.email)
        instance.password = validated_data.get("password", instance.password)
        instance.save()
        return instance


# Serializer class for the SignUpOTP model
class SignUpOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = SignUpOTP
        fields = ["otp", "email"]

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"email": "User does not exist."})

        try:
            user_otp = SignUpOTP.objects.get(user=user)
        except SignUpOTP.DoesNotExist:
            raise serializers.ValidationError({"otp": "OTP does not exist."})

        if user_otp.otp != otp:
            raise serializers.ValidationError({"otp": "Incorrect OTP."})

        data["user"] = user
        data["user_otp"] = user_otp
        return data

    def make_user_active(self):
        user = self.validated_data["user"]
        user.is_active = True
        user.save()

    def delete_otp(self):
        user_otp = self.validated_data["user_otp"]
        user_otp.delete()


class SessionSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"email": "User does not exist."})

        if not user.is_password_valid(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        if not user.is_active:
            raise serializers.ValidationError({"user": "User is not active."})

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        session = Session(user=user)
        session.generate_session_id()
        session.save()
        return session
