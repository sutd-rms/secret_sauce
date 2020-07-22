from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers
from .models import *

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'groups']

class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'cover']
