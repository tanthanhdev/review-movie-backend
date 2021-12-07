
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
        
# Dashboard
class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
    # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False

    def _product_user(self):
        try:
            current_user = self._current_user()
            product = Product.objects.get(Q(title__iexact=self.validated_data['title']), Q(user=current_user))
            return product
        except:
            return None

    def product_exists(self, slug):
        product = self._product_user()
        if product:
            if product.slug != slug:
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

class ProductSerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=True)
    
    class Meta:
        model = Product
        fields = "__all__"
    
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def product_exists(self):
        current_user = self._current_user()
        product = Product.objects.filter(Q(title__iexact=self.validated_data['title']), Q(user=current_user))
        if product:
            return False
        return True  
  
    def create(self, validated_data):
        try: 
            current_user = self._current_user()
            product = Product.objects.create(**validated_data)
            product.user = current_user
            product.save()
            return product
        except:
            return serializers.ValidationError("Bad Request")
        return serializers.ValidationError("Server Error")