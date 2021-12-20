
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
product_list = ProductViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create' # Create a new
})

product_detail = ProductViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

product_unauth_list = ProductUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})

product_unauth_detail = ProductUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
})


urlpatterns = [
    # dashboard
    path('products/', product_list, name='product_list'),
    path('products/<slug:slug>', product_detail, name='product_detail'),
    # Unauthenticated
    path('public/products/', product_unauth_list, name='product_unauth_list'),
    path('public/products/<slug:slug>', product_unauth_detail, name='product_unauth_detail'),
    path('public/products/pagination/', PublicProductPagination.as_view(), name='public_product_pagination'),
    path('public/popularity/products/pagination/', PublicPopularityProductPagination.as_view(), name='public_popularity_product_pagination'),
]