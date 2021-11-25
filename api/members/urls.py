
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# # # Define class
# tag_list = TagViewSet.as_view({
#     'get': 'list', # Get lists
#     'post': 'create' # Create a new
# })

# tag_detail = TagViewSet.as_view({
#     'get': 'retrieve', # get detail
#     # 'patch': 'update', # update
#     # 'delete': 'destroy', # delete
# })

urlpatterns = [
    # # dashboard
    # url(r'^tags.*$', tag_list),
    # # url(r'^tags/delete-all.*$', tag_detail, name='tag_delete_all'),
    # url(r'^tags/<slug:slug>.*$', tag_detail, name='tag_detail'),
]