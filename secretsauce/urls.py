"""secretsauce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


from rest_framework.urlpatterns import format_suffix_patterns

import secretsauce.apps.portal.views as portal_views

from rest_framework.urlpatterns import format_suffix_patterns

import secretsauce.apps.portal.views as portal_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('datablocks/', portal_views.DataBlockList.as_view()),
    path('datablocks/<int:pk>', portal_views.DataBlockDetail.as_view()),
    path('projects/', portal_views.ProjectList.as_view()),
    path('projects/<int:pk>', portal_views.ProjectDetail.as_view()),
    path('constraints/', portal_views.ConstraintList.as_view()),
    path('constraints/<int:pk>', portal_views.ConstraintDetail.as_view()),
    path('predictionmodel/', portal_views.PredictionModelList.as_view()),
    path('predictionmodel/<int:pk>', portal_views.PredictionModelDetail.as_view()),
    path('auth/', include('secretsauce.apps.account.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
