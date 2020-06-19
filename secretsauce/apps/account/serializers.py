from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers
from .models import *

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
