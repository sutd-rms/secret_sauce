from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class DataBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBlock
        fields = ['name', 'upload']