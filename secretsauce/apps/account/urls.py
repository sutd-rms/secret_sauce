from django.urls import path, include
from secretsauce.apps.account import views

urlpatterns =[
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('restricted/', views.restricted)
]