from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class DataBlockHeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataBlockHeader
        fields = ['item_id']

class DataBlockSerializer(serializers.ModelSerializer):
    schema = DataBlockHeaderSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = DataBlock
        fields = '__all__'

class ConstraintParameterSerializer(serializers.ModelSerializer):

    item_name = serializers.CharField(max_length=200, required=False)

    class Meta:
        model = ConstraintParameter
        fields = ['id', 'item_id', 'item_name']

class ConstraintBlockSerializer(serializers.ModelSerializer):
    constraints = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ConstraintBlock
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    data_blocks = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)
    constraint_blocks = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)

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

class TrainedPredictionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainedPredictionModel
        fields = '__all__'

class PredictionModelDisplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = PredictionModel
        fields = ['id', 'name']

class DataBlockDisplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = DataBlock
        fields = ['id', 'name']

class TraindePredictionModelDisplaySerializer(serializers.ModelSerializer):

    prediction_model = PredictionModelDisplaySerializer(required=True, many=False)
    data_block = DataBlockDisplaySerializer(required=True, many=False)

    class Meta:
        model = TrainedPredictionModel
        exclude =[]
