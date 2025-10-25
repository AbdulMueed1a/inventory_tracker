from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm',None)
        if password_confirm is None:
            raise serializers.ValidationError('Password Confirm: required Field missing.')
        if password != password_confirm:
            raise serializers.ValidationError({'Password Confirm':'Passwords do not match'})
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'Email': 'Email already registered'})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'Username': 'Username already registered'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        if password is None:
            raise serializers.ValidationError('Password is required')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
