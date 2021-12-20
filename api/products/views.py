from functools import reduce
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User, Group, Permission
from rest_framework import viewsets
from rest_framework import status
from django.db.models import Q, query
from collections import OrderedDict
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .serializers import ProductSerializer, ProductUpdateSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid
from operator import or_, and_
from django.core import serializers
import datetime

from api.users import status_http
from api.users.custom_pagination import LibraryCustomPagination
# from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    default_serializer_classes = ProductSerializer
    permission_classes = [IsAuthenticated, IsTokenValid]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Product.objects.filter(Q(user=request.user))
            serializer = ProductSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'product': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Product.objects.get(slug=slug, user=request.user)
            serializer = ProductSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'product': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data, context={
            'request': request
        })
        message = {}
        if serializer.is_valid():
            if not serializer.product_exists():
                message['product'] = 'Product with this title already exists'
            if message:
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if not serializer.tag_exists():
                message['tag'] = 'Tag not found'
            if message:
                return Response(message, status=status.HTTP_204_NO_CONTENT)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

    def update(self, request, slug, format=None):
        queryset = None
        try:
            queryset = Product.objects.get(Q(slug=slug), Q(user=request.user))
            data = request.data
            serializer = ProductUpdateSerializer(queryset, data=data, context={
                'request': request
            })
            message = {}
            if serializer.is_valid():
                if not serializer.product_exists(slug):
                    message['product'] = 'Product with this title already exists'
                if message:
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                if not serializer.tag_exists():
                    message['tag'] = 'Tag not found'
                if message:
                    return Response(message, status=status.HTTP_204_NO_CONTENT)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Product Update Not Found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, slug=None, format=None):
        try:
            if not slug:
                queryset = Product.objects.filter(user=request.user)
                if not queryset:
                    return Response({'product': 'Product Not Found'}, status=status.HTTP_204_NO_CONTENT)
                queryset.delete()
                return Response({'message': 'Delete all product successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                queryset = Product.objects.get(Q(slug=slug), Q(user=request.user))
                queryset.delete()
                return Response({'message': 'Delete product successfully'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
    
# Product unauthenticated
class ProductUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Product.objects.all()
            serializer = ProductSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'product': 'Product not found'}, status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, slug=None):
        print('test')
        try:
            queryset = Product.objects.get(slug=slug)
            serializer = ProductSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'product': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
class PublicProductPagination(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []
    pagination_class = LibraryCustomPagination
    
    def get_queryset(self):
        queryset = Product.objects.all()
        genre = self.request.query_params.get('genre')
        english_name = self.request.query_params.get('english_name')
        release_date = self.request.query_params.get('release_date')
        if genre:
            queryset = queryset.filter(genre__name=genre)
        if english_name:
            queryset = queryset.filter(country__english_name=english_name)
        if release_date == "Up Comming":
            queryset = queryset.filter(Q(release_date__gt=datetime.datetime.now()) #greater than
                                       | Q(status="In Production"))
        return queryset

class PublicPopularityProductPagination(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []
    pagination_class = LibraryCustomPagination
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-popularity')
        english_name = self.request.query_params.get('english_name')
        if english_name:
            queryset = queryset.filter(country__english_name=english_name)
        return queryset