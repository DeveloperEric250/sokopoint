import re

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'location',
            'user_type',
            'password',
            'confirm_password',
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        if value:
            value = value.lower()
            if CustomUser.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate_phone(self, value):
        if value:
            normalized = value.replace(' ', '')
            if not re.fullmatch(r'^\+?[0-9]{7,15}$', normalized):
                raise serializers.ValidationError('Enter a valid phone number.')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password or confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
            validate_password(password)

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)

        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            validate_password(password)
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['username'],
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError('Invalid username or password.')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Incorrect current password.'})

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        validate_password(attrs['new_password'])
        return attrs