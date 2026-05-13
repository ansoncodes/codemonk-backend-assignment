from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    # serializer for user registration with password validation

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["name", "email", "date_of_birth", "password", "password2"]

    def validate(self, attrs):
        # ensure both passwords match before proceeding
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # remove password2 and create the user with a hashed password
        validated_data.pop("password2")
        return User.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            date_of_birth=validated_data["date_of_birth"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    # serializer for user login and token generation

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # authenticate the user and attach jwt tokens
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        refresh = RefreshToken.for_user(user)
        attrs["access"] = str(refresh.access_token)
        attrs["refresh"] = str(refresh)
        return attrs
