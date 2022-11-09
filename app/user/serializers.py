from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'nro',
            'profile_picture',
            'is_staff',)
        read_only_fields = ('id', 'profile_picture', 'nro', 'is_staff')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        depth = 1

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
    """Only used in DRF spectacular"""
    class Meta:
        model = get_user_model()
        fields = ("nro",)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for listing all users"""

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "nro",
            "email",
            'first_name',
            'last_name',
            "is_staff")


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


class ProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading profile pictures to Users."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'profile_picture']
        read_only_fields = ['id']
        extra_kwargs = {'profile_picture': {'required': 'True'}}


class UserActiveSerializer(serializers.ModelSerializer):
    """Serializer for changing DB active status of Users."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'is_active']
        read_only_fields = ['id']
        extra_kwargs = {'is_active': {'required': 'True'}}
