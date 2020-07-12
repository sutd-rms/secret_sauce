from rest_framework import generics, status, permissions, mixins, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ParseError

from django.db.models.query import QuerySet
from django.http import FileResponse, Http404

from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.serializers import *
from secretsauce.permissions import IsOwnerOrAdmin, AdminOrReadOnly
from secretsauce.utils import UploadVerifier, CostSheetVerifier

import pandas as pd
from collections import defaultdict

class DataBlockList(generics.ListCreateAPIView):
    """
    List all datablocks or create a new datablock.

    Usage example:
        create: curl -X POST -F "name=test_file" -F "upload=@test.csv" -F "project=<uuid>" localhost:8000/datablocks/
        list: curl localhost:8000/datablocks/
    """
    queryset = DataBlock.objects.all()
    serializer_class = DataBlockSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item_ids = UploadVerifier(request.FILES['upload']).get_schema()
            self.perform_create(serializer, item_ids)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, item_ids):
        data_block = serializer.save()
        schema = DataBlockSchema.objects.create(data_block=data_block)
        header_objects = [DataBlockHeader(schema=schema, item_id=item_id) for item_id in item_ids]
        DataBlockHeader.objects.bulk_create(header_objects)

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        project = self.request.query_params.get('project')
        return queryset.filter(project=project)
        
class DataBlockDetail(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete a datablock instance
    """ 

    permission_classes = [IsOwnerOrAdmin]
    queryset = DataBlock.objects.all()
    serializer_class = DataBlockSerializer

    def retrieve(self, request, pk, *args, **kwargs):
        if self.get_queryset().filter(id=pk):
            upload = self.get_queryset().get(id=pk).upload
            response = FileResponse(upload, status=status.HTTP_200_OK, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{upload.name}.csv"'
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ProjectList(generics.ListCreateAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(owners=user.id)

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsOwnerOrAdmin]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ConstraintBlockList(generics.ListCreateAPIView):
    """
    List all constraint blocks related to a Project
    Create new constraint block
    """

    queryset = ConstraintBlock.objects.all()
    serializer_class = ConstraintBlockSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        project = self.request.query_params.get('project')
        return queryset.filter(project=project)

class ConstraintBlockDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy a ConstraintBlock
    """
    permission_classes = [IsOwnerOrAdmin]
    queryset = ConstraintBlock.objects.all()
    serializer_class = ConstraintBlockSerializer

class ConstraintList(generics.ListCreateAPIView):
    """
    List all constraints related to a ConstraintBlock
    Create a new constraint related to a ConstraintBlock
    """
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        constraint_block = request.query_params.get('constraint_block')
        return queryset.filter(constraint_block=constraint_block)

class ConstraintDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy a constraint
    """
    permission_classes = [IsOwnerOrAdmin]
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

class ConstraintParameterList(generics.ListCreateAPIView):
    """
    List all constraint parameters related to a ConstraintBlock
    """
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
        "'%s' should either include a `queryset` attribute, "
        "or override the `get_queryset()` method."
        % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        constraint_block = request.query_params.get('constraint_block')
        return queryset.filter(constraint_block=constraint_block)

class ConstraintParameterDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy a constraint parameter
    """
    permission_classes = [IsOwnerOrAdmin]
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

class ConstraintRelationshipCreate(generics.CreateAPIView):
    """
    Create ConstraintParameterRelationship
    """
    queryset = ConstraintParameterRelationship.objects.all()
    serializer_class = ConstraintParameterRelationshipSerializer

class ConstraintRelationshipDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy ConstraintParameterRelationship
    """
    permission_classes = [IsOwnerOrAdmin]
    queryset = ConstraintParameterRelationship.objects.all()
    serializer_class = ConstraintParameterRelationshipSerializer

class PredictionModelList(generics.ListCreateAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = PredictionModel.objects.all()
    serializer_class = PredictionModelSerializer

class PredictionModelDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = PredictionModel.objects.all()
    serializer_class = PredictionModelSerializer

class ModelTagList(generics.ListCreateAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = ModelTag.objects.all()
    serializer_class = ModelTagSerializer

class ModelTagDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = ModelTag.objects.all()
    serializer_class = ModelTagSerializer

class ItemDirectoryList(generics.ListCreateAPIView):

    permission_classes = [IsOwnerOrAdmin]
    queryset = ItemDirectory.objects.all()
    serializer_class = ItemDirectorySerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        if 'file' not in request.data:
                raise ParseError(detail='file is required', code='required')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file_obj = request.data['file']
            items = CostSheetVerifier(file_obj).get_items()
            self.perform_create(serializer, items)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, items):
        item_directory = serializer.save()
        item_objs = [Item(item_directory=item_directory, name=name, item_id=item_id, cost=cost) for item_id, (name, cost) in items.items()]
        Item.objects.bulk_create(item_objs)

    def delete(self, request, *args, **kwargs):
        project = request.data['project']
        if not self.get_queryset().filter(project=project).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="ItemDirectory does not exist.")
        instance = self.get_queryset().get(project=project)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

class GetDataBlock(views.APIView):

    parser_classes = [MultiPartParser]
    queryset = DataBlock.objects.all()
    max_query_size = 10

    def get(self, request, pk, *args, **kwargs):
        data_block = self.get_object(pk)

        if 'query' not in request.data or 'items' not in request.data:
            raise ParseError(detail='Query and Items required', code='invalid_data')

        query = request.data.get('query')
        items = request.data.getlist('items')

        if len(items) > self.max_query_size:
            raise ParseError(detail=f'Query is too large, maximum of {self.max_query_size} items only', code='query_size_exceeded')

        
        if query == 'price':
            body = self.obtain_prices(data_block.upload, items)
        elif query == 'quantity':
            body = self.obtain_quantities(data_block.upload, items)
        else:
            raise ParseError(detail="Query is not well specified, please specify 'price' or 'quantity' ", code='invalid_query')

        return Response(body, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            return DataBlock.objects.get(id=pk)
        except DataBlock.DoesNotExist:
            raise Http404

    def obtain_prices(self, file, items):
        df = pd.read_csv(file, encoding='utf-8')
        df = df[df['Item_ID'].isin(items)][['Item_ID', 'Price_']]
        output = defaultdict(list)
        for idx, row in df.iterrows():
            item_id = int(row['Item_ID'])
            price = row['Price_']
            output[item_id].append(price)
        final_output = sorted([(k, v) for k, v in output.items()], key=lambda x: x[0])
        items, datasets = zip(*final_output)
        final_output = {
            'items': items,
            'datasets': datasets
        }
        return final_output

    def obtain_quantities(self, file, items):
        df = pd.read_csv(file, encoding='utf-8')
        df = df[df['Item_ID'].isin(items)]
        output = defaultdict(list)
        weeks = set()
        for idx, row in df.iterrows():
            item_id = int(row['Item_ID'])
            week = int(row['Wk'])
            weeks.add(week)
            qty = row['Qty_']
            while len(output[item_id]) < week:
                output[item_id].append(None)
            output[item_id][week - 1] = qty
        final_output = {
            'weeks': sorted(list(weeks)),
            'datasets': output,
        }
        return final_output