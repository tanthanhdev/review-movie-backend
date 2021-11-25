
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# Define class
search_job_list = SearchJobViewSet.as_view({
    'get': 'list', # Get lists
})

urlpatterns = [
    # dashboard
    path('searches/job/', search_job_list),
]