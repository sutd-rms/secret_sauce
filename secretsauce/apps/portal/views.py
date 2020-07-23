from rest_framework import generics, status, permissions, mixins, views, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ParseError, ValidationError

from django.db.models.query import QuerySet
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from secretsauce.apps.portal.models import *
from secretsauce.apps.portal.serializers import *
from secretsauce.permissions import IsOwnerOrAdmin, AdminOrReadOnly
from secretsauce.utils import UploadVerifier, CostSheetVerifier

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from collections import defaultdict
from threading import Thread
import os, requests, json

FILLET = 'https://fillet.azurewebsites.net'

class DataBlockList(generics.ListCreateAPIView):
    """
    List all datablocks or create a new datablock.

    Usage example:
        create: curl -X POST -F "name=test_file" -F "upload=@test.csv" -F "project=<uuid>" localhost:8000/datablocks/
        list: curl localhost:8000/datablocks/
    """
    queryset = DataBlock.objects.all()
    serializer_class = DataBlockListSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item_ids = UploadVerifier(request.FILES['upload']).get_schema()
            self.perform_create(serializer, item_ids)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, item_ids):
        data_block = serializer.save()
        header_objects = [DataBlockHeader(data_block=data_block, item_id=item_id) for item_id in item_ids]
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
    serializer_class = DataBlockSingleSerializer

class GetDataBlock(views.APIView):

    parser_classes = [MultiPartParser]
    max_query_size = 10

    def get(self, request, pk, *args, **kwargs):
        data_block = self.get_object(pk)

        if 'query' not in request.query_params:
            raise ParseError(detail="'query' required in query_params", code='invalid_data')        
        if 'items' not in request.query_params:
            raise ParseError(detail="'items' required in query_params", code='invalid_data')

        query = request.query_params.get('query')
        items = request.query_params.get('items').split(',')
        try:
            items = list(map(int, items))
        except ValueError as e:
            raise ParseError(e)

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

class ProjectItems(views.APIView):
    """
    Upload or delete list of Items from a Project
    """

    permission_classes = [IsOwnerOrAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), id=pk)
        
        if project.cost_sheet:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cost sheet already uploaded")

        try:
            file_obj = request.data['file']
        except KeyError:
            raise ParseError(detail='file is required', code='required')

        items = CostSheetVerifier(file_obj).get_items()
        self.perform_create(project, items)
        return Response(status=status.HTTP_201_CREATED)

    def perform_create(self, project, items):
        item_objs = [Item(project=project, 
                          name=name, 
                          item_id=item_id, 
                          cost=cost, 
                          price_current=current, 
                          price_floor=floor, 
                          price_cap=cap) for item_id, (name, cost, current, floor, cap) in items.items()]
        Item.objects.bulk_create(item_objs)
        project.cost_sheet = True
        project.save()

    def delete(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), id=pk)
        if not project.cost_sheet:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="No cost sheet to delete")
        self.perform_destroy(project)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.items.all().delete()
        instance.cost_sheet = False
        instance.save()

class ConstraintBlockCreate(generics.CreateAPIView):
    """
    Create new ConstraintBlock from a specified DataBlock schema
    """

    queryset = ConstraintBlock.objects.all()
    serializer_class = ConstraintBlockSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                data_block = DataBlock.objects.get(id=self.request.data['data_block'])
            except KeyError:
                raise ParseError(detail="missing parameter: data_block")
            except DataBlock.DoesNotExist:
                raise Http404
            self.perform_create(serializer)
            constraint_block = get_object_or_404(ConstraintBlock.objects.all(), id=serializer.data['id'])
            constraint_params = [ConstraintParameter(item_id=header.item_id, constraint_block=constraint_block) for header in data_block.schema.all()]
            ConstraintParameter.objects.bulk_create(constraint_params)
            serializer = self.get_serializer(instance=self.get_queryset().get(id=serializer.data['id']))

            project = constraint_block.project
            if project.cost_sheet:
                items = project.items.all()
                for constraint_param in serializer.data['params']:
                    try:
                        item_id = constraint_param.get('item_id')
                        item_name = items.get(item_id=item_id).name
                    except Item.DoesNotExist:
                        item_name = None
                    constraint_param['item_name'] = item_name
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConstraintBlockItems(generics.ListAPIView):
    """
    Retrieve ConstraintParameters associated to a ConstraintBlock
    """
    permission_classes = [IsOwnerOrAdmin]
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        project = ConstraintBlock.objects.get(id=self.kwargs.get('pk')).project
        if project.cost_sheet:
            items = project.items.all()
            for constraint_param in serializer.data:
                try:
                    item_id = constraint_param.get('item_id')
                    item_name = items.get(item_id=item_id).name
                except Item.DoesNotExist:
                    item_name = None
                constraint_param['item_name'] = item_name
        return Response(serializer.data)

    def get_queryset(self):
        cb = ConstraintBlock.objects.get(id=self.kwargs.get('pk'))
        return self.queryset.filter(constraint_block=cb)

class ConstraintListAndCreate(generics.ListCreateAPIView):
    
    queryset = Constraint.objects.all()
    parser_classes =  [JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        cb = self.request.query_params.get('constraint_block')
        return self.queryset.filter(constraint_block=cb)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConstraintDisplaySerializer
        return ConstraintCreateSerializer

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

class TrainModel(generics.ListCreateAPIView):

    queryset = TrainedPredictionModel.objects.all()
    serializer_class = TrainedPredictionModelSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            data_block = DataBlock.objects.get(id=serializer.data['data_block'])
            df = pd.read_csv(data_block.upload, encoding='utf-8', )
            table = pa.Table.from_pandas(df)
            buf = pa.BufferOutputStream()
            pq.write_table(table, buf)
            files = {'data': buf.getvalue()}
            payload = {'cv_acc': True, 'project_id': serializer.data['id']}
            def r(url, data=None, files=None, timeout=None):
                try:
                    resp = requests.post(FILLET+'/train/', data=payload, files=files, timeout=(3.05, 10))
                except requests.exceptions.ReadTimeout: 
                    pass
                except requests.exceptions.ConnectionTimeout:
                    pass
            Thread(target=r,
                args=(FILLET + '/train/', ),
                kwargs={
                    'data': payload,
                    'files': files,
                    'timeout': (3.05, 10),
                }).start()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        try:
            project = Project.objects.get(id=self.request.query_params['project'])
        except KeyError:
            raise ParseError(detail="Please specify project")
        except Project.DoesNotExist:
            raise Http404
        
        data_blocks = project.data_blocks.all()
        trained_models = self.queryset.filter(data_block__in=data_blocks)
        for tm in trained_models:
            if not tm.available:
                payload = json.dumps({'project_id': str(tm.id)})
                headers = {'content-type': 'application/json',
                        'Accept-Charset': 'UTF-8'
                        }
                try:
                    r = requests.post(FILLET + '/query_progress/', data=payload, headers=headers, timeout=1)
                    if json.loads(r.content).get('pct_complete') == 100:
                        tm.available = True
                        tm.save()
                except requests.exceptions.ReadTimeout as e:
                    raise ParseError(e)
                except requests.exceptions.ConnectTimeout as e:
                    raise ParseError(e)
        return trained_models 

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TraindePredictionModelDisplaySerializer
        return TrainedPredictionModelSerializer

class ConstraintCategoryList(generics.ListCreateAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = ConstraintCategory.objects.all()
    serializer_class = ConstraintCategorySerializer

class ConstraintCategoryDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = ConstraintCategory.objects.all()
    serializer_class = ConstraintCategorySerializer