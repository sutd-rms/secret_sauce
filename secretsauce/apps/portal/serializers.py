from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class DataBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBlock
        fields = '__all__'

class ConstraintParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintParameter
        fields = '__all__'

class ConstraintParameterRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintParameterRelationship
        fields = '__all__'

class ConstraintSerializer(serializers.ModelSerializer):
    constraint_relationships = ConstraintParameterRelationshipSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Constraint
        fields = '__all__'

class ConstraintBlockSerializer(serializers.ModelSerializer):
    constraints = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ConstraintBlock
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    data_blocks = DataBlockSerializer(many=True, required=False, read_only=True)
    constraint_blocks = ConstraintBlockSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Project
        fields = '__all__' 

class PredictionModelSerializer(serializers.ModelSerializer):
    model_tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = PredictionModel
        fields = '__all__'
