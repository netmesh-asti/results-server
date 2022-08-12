from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from durin.serializers import APIAccessTokenSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'first_name', 'last_name',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user information"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ListUserRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("ntc_region",)


class ListUsersSerializer(serializers.ModelSerializer):
    """Serializer for listing all users"""

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        model = get_user_model()
        fields = ("ntc_region", "id", "email")
        read_only_fields = ("id", "email",)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the Auth Token Object"""

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    email = serializers.CharField()
    client = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and Authenticate User"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs


class UserTokenSerializer(APIAccessTokenSerializer):
    email = serializers.CharField()
    client = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def get_field_names(self, declared_fields, info):
        print(declared_fields)
        return super().get_field_names(declared_fields, info)
