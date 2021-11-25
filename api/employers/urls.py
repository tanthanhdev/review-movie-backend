
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# # Define class

employer_detail = EmployerViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    # 'delete': 'destroy', # delete
})

public_job_list = PublicEmployerViewSet.as_view({
    'get': 'list', # Get lists
})

public_job_detail = PublicEmployerViewSet.as_view({
    'get': 'retrieve', # get detail
})

urlpatterns = [
    # dashboard
    path('employers/<int:id>/', employer_detail, name='employer_detail'),
    # Unauthenticated
    path('public/employers/', public_job_list, name='public_job_list'),
    path('public/employers/<int:id>', public_job_detail, name='public_job_detail'),
]