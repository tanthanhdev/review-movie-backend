
from django.contrib.auth.models import Group, Permission, update_last_login
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email
from django.utils.text import slugify 
from django.utils.crypto import get_random_string
from django.db.models import Q
from rest_framework import serializers
from rest_framework.fields import NullBooleanField
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import Group
# models
from .models import *
# serializers
# regex
import re
# rest fw jwt settings
from rest_framework_simplejwt.settings import api_settings
# time
from django.utils import timezone
from datetime import datetime, date, time, timedelta
# custom message
from rest_framework.exceptions import APIException
from rest_framework import status

def _is_token_valid(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        return True
    except:
        return False

def get_user_token(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        return user
    except:
        return False

def unique_slugify(slug):
    unique_slug = slug + get_random_string(length=4)
    return unique_slug

class MyMessage(APIException):
    """Readers message class"""
    def __init__(self, msg, attrs):
        APIException.__init__(self, msg)
        self.status_code = attrs.get('status_code')
        self.message = msg
 
class RetriveEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = "__all__"
        
# Dashboard
class JobUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    about = serializers.CharField(required=False)
    preparation_time = serializers.CharField(required=True)
    cooking_time = serializers.CharField(required=True)
    ingredient = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    method = serializers.CharField(required=True)
    comment = serializers.CharField(required=False)
    category_id = serializers.CharField(required=False)
    occasion_id = serializers.CharField(required=False)
    tag_id = serializers.CharField(required=False)
    web_link = serializers.CharField(required=False)
    link = serializers.CharField(required=False)
    class Meta:
        model = Job
        fields = ('id', 'user' ,'title', 'slug', 'about', 'preparation_time', 'cooking_time', 'ingredient', 'image',
                  'method', 'comment', 'web_link', 'link',
                  'category_id', 'job_category_name', 'occasion_id', 'job_occasion_name', 
                  'tag_id',  'job_tag_name')
        
    # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False

    def _job_user(self):
        try:
            current_user = self._current_user()
            job = Job.objects.get(Q(title__iexact=self.validated_data['title']), Q(user=current_user))
            return job
        except:
            return None

    def job_exists(self, slug):
        job = self._job_user()
        if job:
            if job.slug != slug:
                return False
        return True  
    
    def tag_exists(self):
        tag_id = None
        try:
            tag_id = self.validated_data['tag_id']
        except: pass
        if tag_id:
            current_user = self._current_user()
            tag = Tag.objects.filter(Q(id=tag_id), (
                Q(user=current_user) | Q(status=True) | Q(user__is_staff=True)))
            if not tag:
                return False
        return True

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug')

class JobSerializer(serializers.ModelSerializer):
    employer = RetriveEmployerSerializer()
    country = CountrySerializer()
    tag = TagSerializer(many=True)
    
    class Meta:
        model = Job
        fields = "__all__"
    
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def tag_exists(self):
        if (self.validated_data['tag_id']):
            current_user = self._current_user()
            tag = Tag.objects.filter(Q(id=self.validated_data['tag_id']), (
                Q(user=current_user) | Q(status=True) | Q(user__is_staff=True)))
            if not tag:
                return False
            return True
        return True
    
    def job_exists(self):
        current_user = self._current_user()
        job = Job.objects.filter(Q(title__iexact=self.validated_data['title']), Q(user=current_user))
        if job:
            return False
        return True  
  
    def create(self, validated_data):
        try: 
            current_user = self._current_user()
            job = Job.objects.create(**validated_data)
            job.user = current_user
            job.save()
            return job
        except:
            return serializers.ValidationError("Bad Request")
        return serializers.ValidationError("Server Error")