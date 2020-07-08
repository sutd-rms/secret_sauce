from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class DataBlockHeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataBlockHeader
        fields = ['item_id']

class DataBlockSchemaSerializer(serializers.ModelSerializer):
    data_block_headers = DataBlockHeaderSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = DataBlockSchema
        fields = '__all__'

class DataBlockSerializer(serializers.ModelSerializer):
    schema = DataBlockSchemaSerializer(required=False, read_only=True)

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

class ModelTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModelTag
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'

class ItemDirectorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = ItemDirectory
        fields  = '__all__'
