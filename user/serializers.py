from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import MyUser
import re


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Creates a new user.
    Email, username, and password are required.
    Returns a JSON web token.
    """

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).*$", data['password']):
            raise serializers.ValidationError("Password incorrect")

        return data

    # The password must be validated and should not be read by the client
    password = serializers.CharField(
        max_length=12,
        min_length=6,
        write_only=True,
    )

    mail = serializers.CharField(
        max_length=255,
        min_length=5,
        write_only=True,
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = MyUser
        fields = ('mail', 'username', 'password', 'token',)

    def create(self, validated_data):
        return MyUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """
    mail = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=12, write_only=True)

    # Ignore these fields if they are included in the request.
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        mail = data.get('mail', None)
        password = data.get('password', None)

        if mail is None:
            raise serializers.ValidationError(
                'A mail is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(mail=mail, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this mail and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }


class ViewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    mail = serializers.CharField(max_length=30, read_only=True)
