from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from secretsauce.apps.account.models import Token


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def restricted(request, *args, ** kwargs):
#     return Response(data="Display Only for Logged in User", status=status.HTTP_200_OK)

# check whether the token provided is in the database
@api_view(['POST'])
def check_token(request, *args, **kwargs):
    user_token = request.data['token']
    token = Token.objects.filter(token=user_token)
    if token.count()==1:
        print(token[0].company)
        company = token[0].company
        return Response(data={'company': company}, status=status.HTTP_200_OK)
    else:
        return Response(data="Invalid Token!", status=status.HTTP_400_BAD_REQUEST)

# create default entry for Token class, not sure whether this function is necessary
# TODO: move hardcoded company name to static file
@api_view(['GET'])
def add_default_token(request, *args, **kwargs):
    token = Token(token="rms", company="defualt RMS")
    token.save()
    return Response(data="Default token entry added!", status=status.HTTP_200_OK)


# create new RMS token
# TODO: move hardcoded company name to static file
@api_view(['POST'])
def create_token(request, *args, **kwargs):
    print(request.user.token.company)
    if request.user.token.company!= "default RMS":
        return Response(data="Not permitted", status=status.HTTP_401_UNAUTHORIZED)

    token = Token(token=request.data['token'], company=request.data['company'])
    token.save()
    return Response(data={
        "company": "New token created, group: "+request.data['company']
    }, status=status.HTTP_200_OK)