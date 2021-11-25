
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
job_list = JobViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create' # Create a new
})

job_detail = JobViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

job_unauth_list = JobUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})

job_unauth_detail = JobUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
})


urlpatterns = [
    # dashboard
    path('jobs/', job_list, name='job_list'),
    path('jobs/<slug:slug>', job_detail, name='job_detail'),
    # Unauthenticated
    path('public/jobs/', job_unauth_list, name='job_unauth_list'),
    path('public/jobs/<slug:slug>', job_unauth_detail, name='job_unauth_detail'),
]