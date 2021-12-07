from functools import reduce
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User, Group, Permission
from rest_framework import viewsets
from rest_framework import status
from django.db.models import Q, query
from collections import OrderedDict
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from api.products.models import Job
from api.products.serializers import JobSerializer, JobUpdateSerializer
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid
from operator import or_, and_

from api.users import status_http

class SearchJobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    default_serializer_classes = JobSerializer
    permission_classes = []
    pagination_class = None
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        query_string = request.GET.get('q')
        address = request.GET.get('adr')
        slug = request.GET.get('slug')
        if query_string:
            query_string = query_string.strip()
            queryset = Job.objects.filter(Q(title__icontains=query_string) | Q(company_name__icontains=query_string)
                                          | Q(company_location__icontains=query_string) 
                                          | Q(description__icontains=query_string))
            if address:
                address = address.strip()
                if address != "Tất Cả Địa Điểm" and address != "":
                    queryset = Job.objects.filter(Q(company_location=address))
        else:
            queryset = Job.objects.all()
        if slug:
            slug = slug.strip()
            queryset = Job.objects.filter(Q(slug=slug))
        if queryset.count() == 0:
            return Response({'job': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)