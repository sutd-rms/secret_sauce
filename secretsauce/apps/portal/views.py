from rest_framework import generics, status, permissions, mixins, views, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import permission_classes, action
from rest_framework.exceptions import ParseError, ValidationError

from django.db.models.query import QuerySet
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.core.files.base import ContentFile

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
            verifier = UploadVerifier(request.FILES['upload'])
            item_ids = verifier.get_schema()
            self.perform_create(serializer, item_ids)
            return_data = serializer.data
            return_data['errors'] = verifier.errors
            return Response(return_data, status=status.HTTP_201_CREATED)
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

class VizDataBlock(viewsets.ViewSet):

    parser_classes = [MultiPartParser]
    max_query_size = 10

    @action(methods=['get'], detail=True, url_path='vizdata/price', url_name='viz-price')
    def price(self, request, pk, *args, **kwargs):
        data_block = self.get_object(pk)
    
        if 'items' not in request.query_params:
            raise ParseError(detail="'items' required in query_params", code='invalid_data')

        items = request.query_params.get('items').split(',')
        try:
            items = list(map(int, items))
        except ValueError as e:
            raise ParseError(e)

        if len(items) > self.max_query_size:
            raise ParseError(detail=f'Query is too large, maximum of {self.max_query_size} items only', code='query_size_exceeded')

        body = self.obtain_prices(data_block.upload, items)

        return Response(body, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='vizdata/qty', url_name='viz-qty')
    def qty(self, request, pk, *args, **kwargs):
        data_block = self.get_object(pk)
     
        if 'items' not in request.query_params:
            raise ParseError(detail="'items' required in query_params", code='invalid_data')

        items = request.query_params.get('items').split(',')
        try:
            items = list(map(int, items))
        except ValueError as e:
            raise ParseError(e)

        if len(items) > self.max_query_size:
            raise ParseError(detail=f'Query is too large, maximum of {self.max_query_size} items only', code='query_size_exceeded')

        body = self.obtain_quantities(data_block.upload, items)

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
        max_week = 0
        for idx, row in df.iterrows():
            item_id = int(row['Item_ID'])
            week = int(row['Wk'])
            qty = row['Qty_']

            max_week = max(week, max_week)
            while len(output[item_id]) < max_week:
                output[item_id].append(0)

            output[item_id][week - 1] += qty
        final_output = {
            'weeks': list(range(1, max_week + 1)),
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
                          price_floor=floor, 
                          price_cap=cap) for item_id, (name, cost, floor, cap) in items.items()]
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

class ConstraintBlockListCreate(generics.ListCreateAPIView):
    """
    Create new ConstraintBlock from a specified DataBlock schema
    """

    queryset = ConstraintBlock.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                data_block = DataBlock.objects.get(id=self.request.data['data_block'])
                if str(data_block.project.id) != request.data.get('project'):
                    raise ParseError(detail='DataBlock should belong to Project')
            except KeyError:
                raise ParseError(detail="missing parameter: data_block")
            except DataBlock.DoesNotExist:
                raise ParseError(detail="data_block: does not exist")
            self.perform_create(serializer)
            constraint_block = get_object_or_404(ConstraintBlock.objects.all(), id=serializer.data['id'])
            constraint_params = [ConstraintParameter(item_id=header.item_id, constraint_block=constraint_block) for header in data_block.schema.all()]
            ConstraintParameter.objects.bulk_create(constraint_params)
            serializer = self.get_serializer(instance=constraint_block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        project = self.request.query_params.get('project')
        return self.queryset.filter(project=project)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConstraintBlockListDisplaySerializer
        return ConstraintBlockCreateSerializer

class ConstraintBlockDetail(generics.RetrieveDestroyAPIView):

    queryset = ConstraintBlock.objects.all()
    serializer_class = ConstraintBlockDetailSerializer

class ConstraintBlockItems(generics.ListAPIView):
    """
    Retrieve ConstraintParameters associated to a ConstraintBlock
    """
    permission_classes = [IsOwnerOrAdmin]
    queryset = ConstraintParameter.objects.all()
    serializer_class = ConstraintParameterSerializer

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
            constraint_block = ConstraintBlock.objects.get(id=serializer.data.get('constraint_block'))
            constraint_list = constraint_block.get_list()
            price_bounds = constraint_block.project.get_price_bounds()
            payload = json.dumps({
                'constraints': [constraint_list, price_bounds]
            })
            headers = {
                'content-type': 'application/json',
                'Accept-Charset': 'UTF-8'
            }
            try:
                r = requests.post(FILLET + '/detect_conflict/', data=payload, headers=headers)
                if r.status_code == 200:
                    if json.loads(r.content)['conflict'] == 'Conflict exists':
                        serializer.instance.delete()
                        return Response(data='Conflict exists', status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer.instance.delete()
                    raise ParseError(detail='Could not reach constraint conflict checker')
            except requests.exceptions.ReadTimeout as e:
                serializer.instance.delete()
                raise ParseError(detail='Could not reach constraint conflict checker')
            except requests.exceptions.ConnectTimeout as e:
                serializer.instance.delete()
                raise ParseError(detail='Could not reach constraint conflict checker')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        cb = self.request.query_params.get('constraint_block')
        return self.queryset.filter(constraint_block=cb)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConstraintDisplaySerializer
        return ConstraintCreateSerializer

class ConstraintDetail(generics.RetrieveDestroyAPIView):

    queryset = Constraint.objects.all()
    serializer_class = ConstraintDisplaySerializer

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
            model_type = PredictionModel.objects.get(id=serializer.data['prediction_model']).name
            payload = {'cv_acc': True, 'project_id': serializer.data['id'], 'modeltype': model_type}
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
        unavailable = dict()
        for tm in trained_models:
            if tm.pct_complete != 100 or tm.cv_progress != 100 or tm.fi_done == False or tm.ee_done == False:
                unavailable[str(tm.id)] = tm

        payload = json.dumps({
            'project_id_ls': list(unavailable.keys())
        })
        headers = {
            'content-type': 'application/json',
            'Accept-Charset': 'UTF-8',
        }
        try:
            r = requests.post(FILLET + '/batch_query_progress/', data=payload, headers=headers, timeout=3.05)
            if r.status_code == 200:
                for tm_id, data in json.loads(r.content).items():
                    if not (data == 'project not found' or data == 'training not started'):
                        unavailable[tm_id].pct_complete = data.get('pct_complete')
                        unavailable[tm_id].cv_progress = data.get('cv_progress')
                        unavailable[tm_id].fi_done = data.get('fi_done')
                        unavailable[tm_id].ee_done = data.get('ee_done')
                        unavailable[tm_id].save()
                    else:
                        print(data)
        except requests.exceptions.ReadTimeout as e:
            pass
        except requests.exceptions.ConnectTimeout as e:
            pass
        
        return trained_models 

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TraindePredictionModelDisplaySerializer
        return TrainedPredictionModelSerializer

class TrainedModelDetail(generics.RetrieveDestroyAPIView):
    
    queryset = TrainedPredictionModel.objects.all()
    serializer_class = TraindePredictionModelDisplaySerializer

class TrainedModelInfo(viewsets.ViewSet):
    
    queryset = TrainedPredictionModel.objects.all()
    serializer_class = TraindePredictionModelDisplaySerializer
    
    @action(methods=['get'], detail=True)
    def feature_importance(self, request, pk):
        trainedmodel = get_object_or_404(self.queryset, id=pk)
        if trainedmodel.pct_complete != 100:
            raise ParseError(detail='Model has not finished training yet.')
        if trainedmodel.fi_done == False:
            raise ParseError(detail='Feature Importance has not been calculated yet.')
        if not trainedmodel.feature_importance:
            try:
                payload = json.dumps({
                    'project_id': str(trainedmodel.id)
                })
                headers = {
                    'content-type': 'application/json',
                    'Accept-Charset': 'UTF-8'
                }
                r = requests.post(FILLET + '/get_feature_importances/', data=payload, headers=headers, timeout=3.05)
                if r.status_code == 200:
                    records = []
                    for model_id, obj in r.json().items():
                        feature_names = obj['feature_name']
                        importances = obj['importance']
                        for idx in feature_names:
                            record = dict()
                            record['model'] = model_id
                            record['feature_name'] = feature_names[idx]
                            record['importance'] = importances[idx]
                            records.append(record)
                    df = pd.read_json(json.dumps(records), orient='records')
                    file_name = f'{trainedmodel.name}_feature_importance.csv'
                    csv_file = ContentFile(df.to_csv(line_terminator='\n', index=False))
                    trainedmodel.feature_importance.save(file_name, csv_file)
            except Exception as e:
                print(e)
                raise ParseError(e)
        return HttpResponseRedirect(redirect_to=trainedmodel.feature_importance.url, content_type="application/csv")

    @action(methods=['get'], detail=True)
    def elasticity(self, request, pk):
        trainedmodel = get_object_or_404(self.queryset, id=pk)
        if trainedmodel.pct_complete != 100:
            raise ParseError(detail='Model has not finished training yet.')
        if trainedmodel.ee_done == False:
            raise ParseError(detail='Elasticity estimates have not been calculated yet.')
        if not trainedmodel.elasticity:
            try:
                payload = json.dumps({
                    'project_id': str(trainedmodel.id)
                })
                headers = {
                    'content-type': 'application/json',
                    'Accept-Charset': 'UTF-8'
                }
                r = requests.post(FILLET + '/get_elasticity_estimates/', data=payload, headers=headers, timeout=3.05)
                if r.status_code == 200:
                    if 'error' in r.json():
                        raise ParseError(detail=r.json()['error'])
                    records = dict()
                    for price_change_item, ds in r.json().items():
                        for change_type, qty_dict in ds.items():
                            for qty_change_item, qty_change in qty_dict.items():
                                key = str((price_change_item, qty_change_item))
                                if key not in records:
                                    records[key] = dict()
                                    records[key]['price_change_item'] = price_change_item
                                    records[key]['qty_change_item'] = qty_change_item
                                records[key][change_type] = qty_change
                    df = pd.read_json(json.dumps(list(records.values())), orient='records')
                    file_name = f'{trainedmodel.name}_elasticity.csv'
                    csv_file = ContentFile(df.to_csv(line_terminator='\n', index=False))
                    trainedmodel.elasticity.save(file_name, csv_file)
            except Exception as e:
                print(e)
                raise ParseError(e)
        return HttpResponseRedirect(redirect_to=trainedmodel.elasticity.url, content_type="application/csv")

    @action(methods=['get'], detail=True)
    def cv_score(self, request, pk):
        trainedmodel = get_object_or_404(self.queryset, id=pk)
        if trainedmodel.pct_complete != 100:
            raise ParseError(detail='Model has not finished training yet.')
        if trainedmodel.cv_progress != 100:
            raise ParseError(detail='Cross-validation has not been completed.')
        if not trainedmodel.cv_score:
            try:
                payload = json.dumps({
                    'project_id': str(trainedmodel.id)
                })
                headers = {
                    'content-type': 'application/json',
                    'Accept-Charset': 'UTF-8'
                }
                r = requests.post(FILLET + '/get_cv_results/', data=payload, headers=headers, timeout=3.05)
                if r.status_code == 200:
                    json_file = json.dumps(json.loads(r.json()))
                    df = pd.read_json(json_file, orient='columns')
                    file_name = f'{trainedmodel.name}_cv_score.csv'
                    csv_file = ContentFile(df.to_csv(line_terminator='\n', index=False))
                    trainedmodel.cv_score.save(file_name, csv_file)
            except Exception as e:
                print(e)
                raise ParseError(e)
        return HttpResponseRedirect(redirect_to=trainedmodel.cv_score.url, content_type="application/csv")

    @action(methods=['post'], detail=True, parser_classes=[JSONParser])
    def whatif(self, request, pk):
        trainedmodel = get_object_or_404(self.queryset, id=pk)
        if trainedmodel.pct_complete != 100:
            raise ParseError(detail='Model has not finished training yet.')
        prices = request.data['prices']
        items = trainedmodel.data_block.schema.all()
        errors = dict()
        for item in trainedmodel.data_block.schema.all():
            if str(item.item_id) not in prices:
                errors[item.item_id] = "provide price"
            else:
                prices[str(item.item_id)] = float(prices[str(item.item_id)])
        if len(errors) > 0:
            raise ParseError(detail=errors)
        try:
            payload = json.dumps({
                'prices': prices,
                'project_id': str(trainedmodel.id)
            })
            headers = {
                'content-type': 'application/json',
                'Accept-Charset': 'UTF-8'
            }
            r = requests.post(FILLET + '/predict/', data=payload, headers=headers, timeout=10.5)
            return Response(r.json()['qty_estimates'])
        except Exception as e:
            print(e)
            raise ParseError(e)

class ConstraintCategoryList(generics.ListCreateAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = ConstraintCategory.objects.all()
    serializer_class = ConstraintCategorySerializer

class ConstraintCategoryDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [AdminOrReadOnly]
    queryset = ConstraintCategory.objects.all()
    serializer_class = ConstraintCategorySerializer