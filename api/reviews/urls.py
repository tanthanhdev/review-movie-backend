
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *

# # Define class
review_list = ReviewViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create' # Create a new
})

review_detail = ReviewViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

public_review_list = PublicReviewViewSet.as_view({
    'get': 'list', # Get lists
})

public_review_detail = PublicReviewViewSet.as_view({
    'get': 'retrieve', # get detail
})


urlpatterns = [
    # dashboard
    path('reviews/', review_list, name='review_list'),
    path('reviews/<slug:slug>', review_detail, name='review_detail'),
    # Unauthenticated
    path('public/reviews/', public_review_list, name='public_review_list'),
    path('public/reviews/<slug:slug>', public_review_detail, name='public_review_detail'),
]