from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class OwnerSerializer(serializers.Serializer):
    email = serializers.EmailField()

class DataBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBlock
        fields = '__all__'
    
class ProjectSerializer(serializers.ModelSerializer):
    datablocks = DataBlockSerializer(many=True, read_only=True)
    owners = OwnerSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

class ConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constraint
        fields = '__all__'

class ConstraintBlockSerializer(serializers.ModelSerializer):
    constraints = ConstraintSerializer(many=True, read_only=True)

    class Meta:
        model = ConstraintBlock
        fields = '__all__'

class PredictionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionModel
        fields = '__all__'
