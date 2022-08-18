from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'first_name', 'last_name', 'ntc_region')
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


class RetrieveUserRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email',)


class RetrieveUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", 'first_name', 'last_name', "ntc_region", "email")
        read_only_fields = ("ntc_region",)


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
        fields = ("id", "ntc_region", "email", "first_name", "last_name")


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
