from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class DataBlockHeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataBlockHeader
        fields = ['item_id']

class DataBlockListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataBlock
        fields = '__all__'

class DataBlockSingleSerializer(serializers.ModelSerializer):
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
    params = ConstraintParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ConstraintBlock
        fields = '__all__'

class ConstraintParameterRelationshipCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(required=True, queryset=ConstraintParameter.objects.all())
    
    class Meta:
        model = ConstraintParameterRelationship
        fields = ['id', 'coefficient']

class ConstraintCreateSerializer(serializers.ModelSerializer):
    constraint_relationships = ConstraintParameterRelationshipCreateSerializer(many=True)

    class Meta:
        model = Constraint
        fields = ['constraint_block', 'constraint_relationships', 'name', 'in_equality', 'rhs_constant', 'penalty', 'category']

    def create(self, validated_data):
        instance = Constraint.objects.create(
            constraint_block=validated_data['constraint_block'],
            name=validated_data['name'],
            in_equality=validated_data['in_equality'],
            rhs_constant=validated_data['rhs_constant'],
            penalty=validated_data['penalty'],
            category=validated_data['category'],
        )
        relationships = [ConstraintParameterRelationship(
            constraint=instance,
            constraint_parameter=data['id'],
            coefficient=data['coefficient'],
        ) for data in validated_data['constraint_relationships']]
        ConstraintParameterRelationship.objects.bulk_create(relationships)
        return instance


class ConstraintDisplaySerializer(serializers.ModelSerializer):
    equation = serializers.CharField(read_only=True)
    equation_name = serializers.CharField(read_only=True)

    class Meta:
        model = Constraint
        fields = ['id', 'name', 'created', 'penalty', 'equation', 'equation_name', 'category']

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
        exclude = []

class ConstraintCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ConstraintCategory
        fields = ['__all__']