from django.contrib.auth.models import Group, Permission, update_last_login
from django.contrib.auth import authenticate
from .models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email
from django.utils.crypto import get_random_string
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import Group

# models
from api.employers.models import Employer
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

class MyMessage(APIException):
    """Readers message class"""
    def __init__(self, msg, attrs):
        APIException.__init__(self, msg)
        self.status_code = attrs.get('status_code')
        self.message = msg

# User ================================================================
class ChangePasswordSerializer(serializers.ModelSerializer):
    # email = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=False, allow_blank=True)
    old_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['password', 'old_password'] #'email', 
        extra_kwargs = {
            'password': {'write_only': True},
            'old_password': {'write_only': True},
        }

    # def validate(self, data):
    #     old_password = data['old_password']
    #     password = data['password']
    #     # check password
    #     # if len(data['old_password']) < 8:
    #     #     raise serializers.ValidationError(
    #     #         {'message': 'Password must be at least 8 characters.'})
    #     # if len(data['password']) < 8:
    #     #     raise serializers.ValidationError(
    #     #         {'message': 'Password must be at least 8 characters.'})
    #     if len(old_password) < 8 or re.match('\d.*[A-Z]|[A-Z].*\d', old_password) == None:
    #         raise serializers.ValidationError(
    #             {'password': 'Password field must contain at least one capital letter and must be at least 8 characters'})   
    #     if len(password) < 8 or re.match('\d.*[A-Z]|[A-Z].*\d', password) == None:
    #         raise serializers.ValidationError(
    #             {'password': 'Password field must contain at least one capital letter and must be at least 8 characters'})   
    #     return data

    def validate_custom(self, attrs):
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        # Validate required
        if old_password == None and password == None:
            raise MyMessage({
                'old_password': 'This field is required.',
                'password': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif old_password == None:
            raise MyMessage({'old_password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == None:
            raise MyMessage({'password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if old_password == "" and password == "":
            raise MyMessage({
                'old_password': 'This field may not be blank.',
                'password': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif old_password == "":
            raise MyMessage({'old_password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == "":
            raise MyMessage({'password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate password
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', old_password) == None:
            raise MyMessage({
                'password': 'Password field must contain at least one capital letter and must be at least 8 characters'
                             }, {'status_code': status.HTTP_400_BAD_REQUEST})
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password) == None:
            raise MyMessage({
                'password': 'Password field must contain at least one capital letter and must be at least 8 characters'
                             }, {'status_code': status.HTTP_400_BAD_REQUEST})

    def old_password_validate(self, user):
        user = User.objects.get(email=user.email)
        if not user.check_password(self.validated_data['old_password']):
            return False
        return True

    def update(self, user):
        user = User.objects.get(email=user.email)
        password = self.validated_data['password']

        user.set_password(password)
        user.save()
        return user

class ChangeEmailSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {
            'email': {'validators': [EmailValidator]},
        }

     # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False

    def validate_custom(self, attrs):
        email = attrs.get('email')
        # Validate required
        if email == None:
            raise MyMessage({'email': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if email == "":
            raise MyMessage({'email': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate email
        if email:
            if re.match(r'\b[\w.-]+@[\w.-]+.\w{2,4}\b', email) == None:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
            try:
                validate_email(attrs.get("email"))
            except ValidationError:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})

    def update(self, user):
        list_user = User.objects.filter(email=self.validated_data['email'])
        if list_user:  
            # Check new email exist
            return False
        else:
            user = User.objects.get(email=self._current_user().email)
            email = self.validated_data['email']
            
            user.email = email
            user.username = email
            user.save()
            return user
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    default_error_messages = {
        'bad_token': 'Token is incorrect or expired.'
    }
    
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
            # raise MyMessage({'message': 'Token is incorrect or expired.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
            
    
# Authentication ================================================================


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('name',)


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ('name', 'permissions', )


class ResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    access_token = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=False, allow_blank=True)
    confirm_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'access_token']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
            'email': {'validators': [EmailValidator]},
        }

    # def validate(self, data):
    #     password = data['password']
    #     if len(password) < 8 or re.match('\d.*[A-Z]|[A-Z].*\d', password) == None:
    #         raise serializers.ValidationError(
    #             {'password': 'Password field must contain at least one capital letter and must be at least 8 characters'})    
    #     return data

    def validate_custom(self, attrs):
        password = attrs['password']
        confirm_password = attrs['confirm_password']
        access_token = attrs['access_token']
        # Validate required
        if password == None and confirm_password == None and access_token == None:
            raise MyMessage({
                'password': 'This field is required.',
                'confirm_password': 'This field is required.',
                'access_token': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == None and confirm_password == None:
            raise MyMessage({
                'password': 'This field is required.',
                'confirm_password': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == None:
            raise MyMessage({'password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif confirm_password == None:
            raise MyMessage({'confirm_password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif access_token == None:
            raise MyMessage({'access_token': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if password == "" and confirm_password == "" and access_token == "":
            raise MyMessage({
                'password': 'This field may not be blank.',
                'confirm_password': 'This field may not be blank.',
                'access_token': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == "" and confirm_password == "":
            raise MyMessage({
                'password': 'This field may not be blank.',
                'confirm_password': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == "":
            raise MyMessage({'password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif confirm_password == "":
            raise MyMessage({'confirm_password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif access_token == "":
            raise MyMessage({'access_token': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate password
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password) == None and \
            (len(confirm_password) < 8 or re.match('\d.*[A-Z]|[A-Z].*\d', confirm_password) == None):
            raise MyMessage({
            'password': 'Password field must contain at least one capital letter and must be at least 8 characters',
            'confirm_password': 'Password field must contain at least one capital letter and must be at least 8 characters'
                            }, {'status_code': status.HTTP_400_BAD_REQUEST})
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password) == None:
            raise MyMessage({
                'password': 'Password field must contain at least one capital letter and must be at least 8 characters'
                             }, {'status_code': status.HTTP_400_BAD_REQUEST})
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', confirm_password) == None:
            raise MyMessage({
                'confirm_password': 'Password field must contain at least one capital letter and must be at least 8 characters'
                             }, {'status_code': status.HTTP_400_BAD_REQUEST})

    def is_token_valid(self):
        # return _is_token_valid(self, self.validated_data['access_token'])
        try:
            access_token = self.validated_data['access_token']
            _access_token = AccessToken(access_token)
            user_id = _access_token['user_id']
            user = User.objects.get(id=user_id)
            if user.forgot_password_token and access_token == user.forgot_password_token:
                return True
            else:
                return False
        except:
            return False

    def confirm_password_validate(self):
        if self.validated_data['password'] != self.validated_data['confirm_password']:
            return False
        return True

    def change_password(self):
        # user = User.objects.get(email=self.validated_data['email'])
        access_token = self.validated_data['access_token']
        _access_token = AccessToken(access_token)
        user_id = _access_token['user_id']
        user = User.objects.get(id=user_id)
        password = self.validated_data['password']
        user.set_password(password)
        user.forgot_password_token = None
        user.save()
        return user

class CreateAccessTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {
            'email': {'validators': [EmailValidator]},
        }

    def is_account_active(self):
        try:
            user = User.objects.get(
                email=self.validated_data['email'], is_active=True)
            return True
        except:
            return False

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data['email'])
            return True
        except:
            return False

    def get_user(self):
        try:
            return User.objects.get(email=self.validated_data['email'])
        except:
            return None


# class ActiveAccountSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['email']
#         extra_kwargs = {
#             'email': {'validators': [EmailValidator]},
#         }

#     def is_account_active(self):
#         try:
#             user = User.objects.get(
#                 email=self.validated_data['email'], is_active=True)
#             return True
#         except:
#             return False

#     def is_email_exist(self):
#         try:
#             user = User.objects.get(email=self.validated_data['email'])
#             return True
#         except:
#             return False

#     def save(self):
#         user = User.objects.get(email=self.validated_data['email'])
#         user.is_active = True
#         user.save()
#         return user

#     def is_token_valid(self, access_token):
#         return _is_token_valid(self, access_token)

class ActiveAccountSerializer(serializers.Serializer):

    def is_account_active(self, user):
        try:
            user = User.objects.get(email=user.email, is_active=True)
            return True
        except:
            return False

    def save(self, user):
        user.is_active = True
        user.email_verified = True
        user.save()
        return user

    def is_token_valid(self, access_token):
        return _is_token_valid(self, access_token)

class ResendActivationLinkSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {
            'email': {'validators': [EmailValidator]},
        }

    def is_account_active(self):
        try:
            user = User.objects.get(
                email=self.validated_data['email'], is_active=True)
            return True
        except:
            return False

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data['email'])
            return True
        except:
            return False

    def send_mail(self):
        user = User.objects.get(email=self.validated_data['email'])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        link_active = settings.FRONTEND_SITE_URL_ACTIVE_ACCOUNT + \
            ''.join(access_token)
        print(link_active)
        message = render_to_string(
            'api/mail/resend_link_active_account.html', {'link_active': link_active})
        send = EmailMessage('CRUD-Templage', message,
                            from_email=settings.EMAIL_FROM, to=[self.validated_data['email']])
        send.content_subtype = 'html'
        send.send()

        return True


class ForgotPasswordSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True)
    email = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {
            'email': {'validators': [EmailValidator]},
        }

    def validate_custom(self, attrs):
        # Validate required
        if attrs.get("email") == None:
            raise MyMessage({'email': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if attrs.get("email") == "":
            raise MyMessage({'email': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
       
        # Validate email
        if attrs.get("email"):
            try:
                validate_email(attrs.get("email"))
            except ValidationError:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})

    def is_account_active(self):
        try:
            user = User.objects.get(
                email=self.validated_data['email'], is_active=True)
            return True
        except:
            return False

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data['email'])
            return True
        except:
            return False

    def send_mail(self):
        user = User.objects.get(email=self.validated_data['email'])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user.forgot_password_token = access_token
        user.save()

        link_active = settings.FRONTEND_SITE_URL_RESET_PASSWORD + \
            ''.join(access_token)
        message = render_to_string('api/mail/forgot_password.html', {'link_active': link_active, 'user': user})
        email_subject = 'Request to reset your password'
        send = EmailMessage(email_subject, message,
                            from_email=settings.EMAIL_FROM, to=[self.validated_data['email']])
        send.content_subtype = 'html'
        send.send()
        return True
        


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    inviteEmail = serializers.EmailField(required=False)
    inviteBy = serializers.EmailField(required=False)
    email = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    # change field name
    # name = serializers.CharField(source='first_name', required=False, allow_blank=True)
    #more
    status = serializers.CharField(required=False, allow_blank=True)
    #hide
    group = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'status',
                    'group',
                  'inviteEmail', 'inviteBy']  # 'username', 'name',
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'validators': [EmailValidator]},
        }

    def validate_custom(self, attrs):
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        email = attrs.get('email')
        password = attrs.get('password')
        # Validate required
        if first_name == None and last_name == None and email == None and password == None:
            raise MyMessage({
                'first_name': 'This field is required.',
                'last_name': 'This field is required.',
                'email': 'This field is required.',
                'password': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == None and last_name==None and email == None:
            raise MyMessage({
                'first_name': 'This field is required.',
                'last_name': 'This field is required.',
                'email': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == None and last_name == None:
            raise MyMessage({
                'first_name': 'This field is required.',
                'last_name': 'This field is required.',
            }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == None:
            raise MyMessage({'first_name': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif last_name == None:
            raise MyMessage({'last_name': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif email == None:
            raise MyMessage({'email': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == None:
            raise MyMessage({'password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if first_name == "" and last_name == "" and email == "" and password == "":
            raise MyMessage({
                'first_name': 'This field may not be blank.',
                'last_name': 'This field may not be blank.',
                'email': 'This field may not be blank.',
                'password': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == "" and last_name=="" and email == "":
            raise MyMessage({
                'first_name': 'This field may not be blank.',
                'last_name': 'This field may not be blank.',
                'email': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == "" and last_name == "":
            raise MyMessage({
                'first_name': 'This field may not be blank.',
                'last_name': 'This field may not be blank.',
            }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == "":
            raise MyMessage({'first_name': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif last_name == "":
            raise MyMessage({'last_name': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif email == "":
            raise MyMessage({'email': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == "":
            raise MyMessage({'password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate email
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})

    def is_email_exist(self):
        try:
            user = User.objects.get(username=self.validated_data['email'])
            if 'inviteEmail' in self.validated_data and 'inviteBy' in self.validated_data and self.validated_data['inviteEmail'] == self.validated_data['email']:
                if user.is_active == True:
                    return 'Invitation has expired or you have already used it'
                # Create Student of coach
                inviteEmail = self.validated_data['inviteEmail']
                inviteBy = self.validated_data['inviteBy']
                try:
                    StudentsOfCoach.objects.get(coach__email=inviteBy, member__email=inviteEmail)
                    return False
                except:
                    return 'Email exist!'
            return 'Email exist!'
        except:
            return False

    def save(self):
        password = self.validated_data['password']
        group = self.validated_data['group']

        # validate password
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password) == None:
            raise serializers.ValidationError(
                {'password': 'Password field must contain at least one capital letter and must be at least 8 characters'})
            
        # if 'inviteEmail' in self.validated_data:
        #     user = User.objects.get(email=self.validated_data['inviteEmail'])
        #     user.email = self.validated_data['email']
        #     user.username = self.validated_data['email']
        #     user.first_name = self.validated_data['first_name']
        #     user.last_name = self.validated_data['last_name']
        #     user.save()
        # else:
        #     user = User.objects.create(
        #         email=self.validated_data['email'],
        #         username=self.validated_data['email'],
        #         first_name=self.validated_data['first_name'],
        #         last_name=self.validated_data['last_name']
        #     )
        # if 'inviteEmail' in self.validated_data:
        #     user = User.objects.get(email=self.validated_data['inviteEmail'])
        #     user.email = self.validated_data['email']
        #     user.username = self.validated_data['email']
        #     user.first_name = self.validated_data['first_name']
        #     user.last_name = self.validated_data['last_name']
        #     user.save()
        # else:
        user = User.objects.create(
            email=self.validated_data['email'],
            username=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )
        if group == "employer":
            Employer.objects.create(user=user).save()
            user.status = self.validated_data['status']
            user.is_staff = True
        else:
            user.is_staff = False
        # save user
        user.set_password(password)
        user.is_active = False # is True if confirmed account,
        user.save()
        
        return user
    
    def send_mail(self):
        user = User.objects.get(email=self.validated_data['email'])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user.forgot_password_token = access_token
        user.save()

        link_active = settings.FRONTEND_SITE_URL_ACTIVE_ACCOUNT + \
            ''.join(access_token)
        message = render_to_string('api/mail/activate.html', {'link_active': link_active, 'user': user})
        email_subject = 'Verify your email address for ' + user.email
        send = EmailMessage(email_subject, message,
                            from_email=settings.EMAIL_FROM, to=[self.validated_data['email']])
        send.content_subtype = 'html'
        send.send()
        return True

class RegistrationEmployerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    inviteEmail = serializers.EmailField(required=False)
    inviteBy = serializers.EmailField(required=False)
    email = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    # change field name
    # name = serializers.CharField(source='first_name', required=False, allow_blank=True)
    #more
    phone_number = serializers.CharField(required=True)
    company_name = serializers.CharField(required=True)
    company_location = serializers.CharField(required=True)
    status = serializers.CharField(required=False, allow_blank=True)
    #hide
    group = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'status',
                  'company_name', 'company_location', 'group',
                  'inviteEmail', 'inviteBy']  # 'username', 'name',
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'validators': [EmailValidator]},
        }

    def validate_custom(self, attrs):
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        email = attrs.get('email')
        password = attrs.get('password')
        # Validate required
        if first_name == None and last_name == None and email == None and password == None:
            raise MyMessage({
                'first_name': 'This field is required.',
                'last_name': 'This field is required.',
                'email': 'This field is required.',
                'password': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == None and last_name==None and email == None:
            raise MyMessage({
                'first_name': 'This field is required.',
                'last_name': 'This field is required.',
                'email': 'This field is required.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == None and last_name == None:
            raise MyMessage({
                'first_name': 'This field is required.',
                'last_name': 'This field is required.',
            }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == None:
            raise MyMessage({'first_name': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif last_name == None:
            raise MyMessage({'last_name': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif email == None:
            raise MyMessage({'email': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == None:
            raise MyMessage({'password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if first_name == "" and last_name == "" and email == "" and password == "":
            raise MyMessage({
                'first_name': 'This field may not be blank.',
                'last_name': 'This field may not be blank.',
                'email': 'This field may not be blank.',
                'password': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == "" and last_name=="" and email == "":
            raise MyMessage({
                'first_name': 'This field may not be blank.',
                'last_name': 'This field may not be blank.',
                'email': 'This field may not be blank.'
                }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == "" and last_name == "":
            raise MyMessage({
                'first_name': 'This field may not be blank.',
                'last_name': 'This field may not be blank.',
            }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif first_name == "":
            raise MyMessage({'first_name': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif last_name == "":
            raise MyMessage({'last_name': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif email == "":
            raise MyMessage({'email': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif password == "":
            raise MyMessage({'password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate email
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})

    def is_email_exist(self):
        try:
            user = User.objects.get(username=self.validated_data['email'])
            if 'inviteEmail' in self.validated_data and 'inviteBy' in self.validated_data and self.validated_data['inviteEmail'] == self.validated_data['email']:
                if user.is_active == True:
                    return 'Invitation has expired or you have already used it'
                # Create Student of coach
                inviteEmail = self.validated_data['inviteEmail']
                inviteBy = self.validated_data['inviteBy']
                try:
                    StudentsOfCoach.objects.get(coach__email=inviteBy, member__email=inviteEmail)
                    return False
                except:
                    return 'Email exist!'
            return 'Email exist!'
        except:
            return False

    def save(self):
        password = self.validated_data['password']
        group = self.validated_data['group']

        # validate password
        if re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password) == None:
            raise serializers.ValidationError(
                {'password': 'Password field must contain at least one capital letter and must be at least 8 characters'})
            
        # if 'inviteEmail' in self.validated_data:
        #     user = User.objects.get(email=self.validated_data['inviteEmail'])
        #     user.email = self.validated_data['email']
        #     user.username = self.validated_data['email']
        #     user.first_name = self.validated_data['first_name']
        #     user.last_name = self.validated_data['last_name']
        #     user.save()
        # else:
        #     user = User.objects.create(
        #         email=self.validated_data['email'],
        #         username=self.validated_data['email'],
        #         first_name=self.validated_data['first_name'],
        #         last_name=self.validated_data['last_name']
        #     )
        # if 'inviteEmail' in self.validated_data:
        #     user = User.objects.get(email=self.validated_data['inviteEmail'])
        #     user.email = self.validated_data['email']
        #     user.username = self.validated_data['email']
        #     user.first_name = self.validated_data['first_name']
        #     user.last_name = self.validated_data['last_name']
        #     user.save()
        # else:
        user = User.objects.create(
            email=self.validated_data['email'],
            username=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )
        if group == "employer":
            Employer.objects.create(user=user).save()
            user.phone_number = self.validated_data['phone_number']
            user.employer.company_name = self.validated_data['company_name']
            user.employer.company_location = self.validated_data['company_location']
            user.status = self.validated_data['status']
            user.is_staff = True
        else:
            user.is_staff = False
        # save user
        user.set_password(password)
        user.is_active = False # is True if confirmed account,
        user.save()
        
        return user
    
    def send_mail(self):
        user = User.objects.get(email=self.validated_data['email'])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user.forgot_password_token = access_token
        user.save()

        link_active = settings.FRONTEND_SITE_URL_ACTIVE_ACCOUNT + \
            ''.join(access_token)
        message = render_to_string('api/mail/activate.html', {'link_active': link_active, 'user': user})
        email_subject = 'Verify your email address for ' + user.email
        send = EmailMessage(email_subject, message,
                            from_email=settings.EMAIL_FROM, to=[self.validated_data['email']])
        send.content_subtype = 'html'
        send.send()
        return True

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'username']

    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate_custom(self, attrs):
        msgError = 'No active account found with the given credentials.'
        credentials = {
            'username': '',
            'email': '',
            'password': attrs.get("password")
        }
        # Validate required
        if attrs.get("email") == None and attrs.get("password") == None:
                raise MyMessage({
                    'email': 'This field is required.',
                    'password': 'This field is required.'
                    }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("username") == None and attrs.get("password") == None:
                raise MyMessage({
                    'username': 'This field is required.',
                    'password': 'This field is required.'
                    }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("email") == None and attrs.get("username") == None:
            raise MyMessage({'username': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("password") == None:
            raise MyMessage({'password': 'This field is required.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate blank
        if attrs.get("email") == "" and attrs.get("password") == "":
                raise MyMessage({
                    'email': 'This field may not be blank.',
                    'password': 'This field may not be blank.'
                    }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("username") == "" and attrs.get("password") == "":
                raise MyMessage({
                    'username': 'This field may not be blank.',
                    'password': 'This field may not be blank.'
                    }, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("email") == "":
            raise MyMessage({'email': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("username") == "":
            raise MyMessage({'username': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        elif attrs.get("password") == "":
            raise MyMessage({'password': 'This field may not be blank.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate email
        if attrs.get("email"):
            try:
                validate_email(attrs.get("email"))
            except ValidationError:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        if attrs.get("username"):
            try:
                validate_email(attrs.get("username"))
            except ValidationError:
                raise MyMessage({'email': 'Enter a valid email address.'}, {'status_code': status.HTTP_400_BAD_REQUEST})
        user_obj = User.objects.filter(email=attrs.get("username")).first(
        ) or User.objects.filter(username=attrs.get("username")).first(
        ) or User.objects.filter(email=attrs.get("email")).first(
        ) or User.objects.filter(username=attrs.get("email")).first()
        if user_obj:
            credentials['username'] = user_obj.username
            credentials['email'] = user_obj.email
        else:
            raise MyMessage({"message": msgError}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate login
        if credentials['username'] and credentials['password']:
            user = authenticate(request=self.context.get('request'),
                                username=credentials['username'], password=credentials['password'])
            if not user:
                raise MyMessage({"message": msgError}, {'status_code': status.HTTP_400_BAD_REQUEST})
            else: 
                # data = super().validate(attrs)
                data = {}

                refresh = self.get_token(user)
                
                if api_settings.UPDATE_LAST_LOGIN:
                            update_last_login(None, self.user)
                
                data['message'] = "Login success"
                data['results'] = {
                    'user': {
                        "id": user_obj.id,
                        "email": user_obj.email,
                        "first_name": user_obj.first_name,
                        "last_name": user_obj.last_name,
                        "is_active": user_obj.is_active,
                        "is_staff": user_obj.is_staff,
                    },
                    # 'refresh': str(refresh),
                    'access_token': str(refresh.access_token),
                    'token_type': "Bearer",
                    'expires_in': (timezone.now() + timedelta(api_settings.ACCESS_TOKEN_LIFETIME.days)).timestamp(),
                    'created_at': timezone.now(),
                }
                # save token in database
                user_obj.token = data['results']['access_token']
                user_obj.expired = datetime.fromtimestamp(data['results']['expires_in'])
                user_obj.save()
                return data
        # return super().validate(credentials)
   
class MySimpleJWTSerializer(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)
    #     user_obj = User.objects.get(username=user)
    #     #
    #     token['email'] = user_obj.email
    #     token['first_name'] = user_obj.first_name
    #     token['last_name'] = user_obj.last_name
    #
    # groups = Group.objects.filter(user=user_obj)
    # roles = ''
    # for g in groups:
    #     roles += g.name + ';'
    # token['roles'] = roles
    # return token

    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        msgError = 'No active account found with the given credentials.'
        credentials = {
            'username': '',
            'password': attrs.get("password")
        }
        user_obj = User.objects.filter(email=attrs.get("username")).first(
        ) or User.objects.filter(username=attrs.get("username")).first()
        if user_obj:
            credentials['username'] = user_obj.username
        else:
            raise MyMessage({"message": msgError}, {'status_code': status.HTTP_400_BAD_REQUEST})
        # Validate login
        if credentials['username'] and credentials['password']:
            user = authenticate(request=self.context.get('request'),
                                username=credentials['username'], password=credentials['password'])
            if not user:
                raise MyMessage({"message": msgError}, {'status_code': status.HTTP_400_BAD_REQUEST})
            else: 
                # data = super().validate(attrs)
                data = {}

                refresh = self.get_token(user)
                
                if api_settings.UPDATE_LAST_LOGIN:
                            update_last_login(None, self.user)
                data['message'] = "Login success"
                data['results'] = {
                    'user': {
                        "id": user_obj.id,
                        "email": user_obj.email,
                        "name": user_obj.first_name,
                    },
                    #'refresh': str(refresh),
                    'access_token': str(refresh.access_token),
                    'token_type': "Bearer",
                    'expires_in': int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
                    'created_at': timezone.now(),
                }
                return data
        # return super().validate(credentials)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MySimpleJWTSerializer