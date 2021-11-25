from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.contrib.auth.models import Group, Permission
from django.db.models import Q, query
from collections import OrderedDict
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .serializers import ChangePasswordSerializer, RegistrationSerializer, ForgotPasswordSerializer, \
                        ResendActivationLinkSerializer, ActiveAccountSerializer, CreateAccessTokenSerializer, \
                        ResetPasswordSerializer, GroupSerializer, \
                        LoginSerializer, ChangeEmailSerializer, LogoutSerializer, RegistrationEmployerSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
import json
from django.core.serializers.json import DjangoJSONEncoder
from .permissions import IsTokenValid

from . import status_http


# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsTokenValid])
# def dashboard_view(request):
#     if request.method == 'GET':
#         currentUser = request.user
#         myRole = None
#         studentsOfCoachFilter = None
#         if currentUser.groups.filter(name=settings.GROUP_NAME['MEMBER']).exists():
#             myRole = settings.GROUP_NAME['MEMBER']
#             studentsOfCoachFilter = {'member': currentUser}
#         if currentUser.groups.filter(name=settings.GROUP_NAME['COACH']).exists():
#             myRole = settings.GROUP_NAME['COACH']
#             studentsOfCoachFilter = {'coach': currentUser}

#         if myRole is None:
#             return Response({'message': 'Current User No Role'}, status=status.HTTP_400_BAD_REQUEST)

#         # response data
#         data = {
#         }

#         return Response(data, status=status.HTTP_200_OK)            
#     return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

# User ==========================================================

# @api_view(['GET'])
# def get_group_with_permission_view(request):
#     if request.method == 'GET':
#         groups = Group.objects.all()
#         serializer = GroupSerializer(groups, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)            
#     return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTokenValid])
def get_user_info_view(request):
    if request.method == 'GET':
        data = {}
        user = request.user
        data['id'] = user.id
        data['email'] = user.email
        data['name'] = user.first_name
        return Response(data, status=status.HTTP_200_OK)
    return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
        

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsTokenValid])
# def get_profile_view(request):
#     if request.method == 'GET':
#         data = {}        
#         data['email'] = request.user.email
#         user = User.objects.get(email=request.user.email)
#         data['first_name'] = user.first_name
#         data['last_name'] = user.last_name
#         data['id'] = user.id
#         groups = Group.objects.filter(user=request.user).all()
#         groups_ = []
#         for g in groups:
#             groups_.append(g.name) ## += g.name + ';'
#         data['groups'] = groups_   
#         # 
#         permissions = Permission.objects.filter(Q(user=user) | Q(group__user=user)).all()
#         permissions_user = []
#         for p in permissions:            
#             permissions_user.append(p.name)
#         data['permissions'] = permissions_user
#         # 
#         # groups_all = Group.objects.all()
#         # serializer_group_all = GroupSerializer(groups_all, many=True)
#         # data['groups_with_permissions'] = serializer_group_all.data
#         # 
#         profile = {}
#         try:
#             profile = ProfileSerializer(user.profile).data
#         except:
#             pass
#         data['profile'] = profile
#         # 
#         data['video_course_is_paid'] = False
#         payment = PaymentLogVideoCourse.objects.filter(user=request.user, video_course_price__isnull=False, category_course__isnull=True).order_by('created_at')
#         if len(payment) > 0:
#             data['video_course_is_paid'] = payment.last().paid 
#         video_course_payment_log_all = {}
#         try:
#             payment = PaymentLogVideoCourse.objects.filter(user=request.user).order_by('created_at')
#             video_course_payment_log_all = PaymentLogVideoCourseSimpleSerializer(payment, many=True).data
#         except Exception as error:
#             print("get_profile_view: ", str(error))
#             pass
#         data['video_course_payment_log_all'] = video_course_payment_log_all        
#         # swing token
#         data['token'] = 0
#         try:
#             data['token'] = GolfSwingToken.objects.filter(Q(user=request.user) & Q(used=False) & Q(valid_till__gte=now())).count()
#         except Exception as error:
#             print("get_profile_view: ", str(error))
#         # swing history
#         golf_swing_payment_log = GolfSwingPaymentLog.objects.filter(
#                 Q(user=request.user) & 
#                 Q(payment_type__type=GolfSwingPaymentItem.MEMBERSHIP_TYPE) & 
#                 Q(ended_at__isnull=True)
#             ).first()
#         data['membership_token_log'] = None
#         if golf_swing_payment_log:
#             data['membership_token_log'] = GolfSwingPaymentLogSerializer(golf_swing_payment_log).data

#         return Response(data, status=status.HTTP_200_OK)            
#     return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)  


# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsTokenValid])
# def update_user_profile_view(request):
#     if request.method == 'POST':
#         # update current user by email
#         # request.data['email'] = request.user.email
#         serializer = UpdateProfileSerializer(data=request.data, context={
#             'request': request
#         })
#         data = {}
#         if serializer.is_valid():
#             try:
#                 if serializer.is_email_exist():
#                     data['message'] = 'Email exist!'
#                     return Response(data, status=status_http.HTTP_ME_450_EMAIL_EXIST) 
#                 serializer.save()
#                 data['email'] = request.data['email']
#                 data['message'] = 'Update profile successfully'
#                 return Response(data, status=status.HTTP_200_OK)
#             except:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)  

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTokenValid])
def change_password_view(request):
    if request.method == 'PUT':
        serializer = ChangePasswordSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.validate_custom(request.data)
            try:
                user = request.user
                if not serializer.old_password_validate(user):
                    data['old_password'] = 'Old password is incorrect'
                    return Response(data, status=status_http.HTTP_ME_454_OLD_PASSWORD_IS_INCORRECT)
                serializer.update(user)
                data['message'] = 'Change password successfully'
                return Response(data, status=status.HTTP_200_OK)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)    

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTokenValid])
def change_email_view(request):
    if request.method == 'PUT':
        serializer = ChangeEmailSerializer(data=request.data, context={
            'request': request
        })
        data = {}
        if serializer.is_valid():
            serializer.validate_custom(request.data)
            try:
                if not serializer.update(request.user):
                    data['email'] = 'Email already exists. Please choose a different email'
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                data['email'] = request.data['email']
                data['message'] = 'Change email successfully'
                return Response(data, status=status.HTTP_200_OK)
            except:
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)    
            
# Authentication ==========================================================

@api_view(['PUT'])
def reset_password_view(request):
    if request.method == 'PUT':
        serializer = ResetPasswordSerializer(data=request.data)
        data = {}
        serializer.validate_custom(request.data)
        if serializer.is_valid():
            if not serializer.is_token_valid():
                data['message'] = 'Token is incorrect or expired'
                return Response(data, status=status_http.HTTP_ME_455_TOKEN_INCORRECT_OR_EXPIRED) 
            if not serializer.confirm_password_validate():
                data['confirm_password'] = 'Password does not match'
                return Response(data, status=status.HTTP_400_BAD_REQUEST) 
            user = serializer.change_password()
            data['email'] = user.email
            data['message'] = 'Reset password successfully!'
            return Response(data, status=status.HTTP_200_OK)
        # else:
        #     data['message'] = ['Token has expired']
        #     return Response(data, status=status.HTTP_400_BAD_REQUEST) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_access_token_view(request):
    if request.method == 'POST':
        serializer = CreateAccessTokenSerializer(data=request.data)
        data = {}        
        if serializer.is_valid():
            if not serializer.is_email_exist():
                data['message'] = 'Email does not exist!'
                return Response(data, status=status_http.HTTP_ME_451_EMAIL_DOES_NOT_EXIST) 
            # if serializer.is_account_active():
            #     data['message'] = 'The account is activated. Please login!'
            #     return Response(data, status=status_http.HTTP_ME_452_ACCOUNT_IS_NOT_ACTIVATED)  
            refresh = RefreshToken.for_user(serializer.get_user())
            access_token = str(refresh.access_token)       
            data['access_token'] = access_token                
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def active_account_view(request):
    if request.method == 'POST':
        serializer = ActiveAccountSerializer(data=request.data)
        data = {}
        # access_token = request.headers['x-access-token']
        access_token = request.data['access_token']
        if serializer.is_valid():
            user = get_user_token(request.data, access_token)
            if serializer.is_account_active(user):
                data['message'] = 'The account is activated already. Please login!'
                return Response(data, status=status_http.HTTP_ME_453_ACCOUNT_IS_ACTIVATED)
            if not serializer.is_token_valid(access_token):
                data['message'] = 'Token is incorrect or expired!'
                return Response(data, status=status_http.HTTP_ME_455_TOKEN_INCORRECT_OR_EXPIRED) 
            serializer.save(user)
            data['email'] = user.email
            data['message'] = 'Activate account successfully!'
            return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def resend_link_activation_view(request):
    if request.method == 'POST':
        serializer = ResendActivationLinkSerializer(data=request.data)
        data = {}        
        if serializer.is_valid():
            if not serializer.is_email_exist():
                data['message'] = 'Email does not exist!'
                return Response(data, status=status_http.HTTP_ME_451_EMAIL_DOES_NOT_EXIST) 
            if serializer.is_account_active():
                data['message'] = 'The account is activated already. Please login!'
                return Response(data, status=status_http.HTTP_ME_453_ACCOUNT_IS_ACTIVATED)     
            if serializer.send_mail():
                data['message'] = 'Send an activation link to your email successfully!'                
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def forgot_password_view(request):
    if request.method == 'POST':
        serializer = ForgotPasswordSerializer(data=request.data)
        data = {}
        serializer.validate_custom(request.data)
        if serializer.is_valid():
            if not serializer.is_email_exist():
                data['email'] = 'Email does not exist!'
                return Response(data, status=status_http.HTTP_ME_451_EMAIL_DOES_NOT_EXIST) 
            if not serializer.is_account_active():
                data['message'] = 'The account is not activated. Please active it!'
                return Response(data, status=status_http.HTTP_ME_452_ACCOUNT_IS_NOT_ACTIVATED)     
            if serializer.send_mail():
                data['message'] = 'Send an activation link to your email successfully!'              
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}        
        serializer.validate_custom(request.data)
        if serializer.is_valid():
            check_exist = serializer.is_email_exist()
            if check_exist:
                data['email'] = check_exist
                return Response(data, status=status_http.HTTP_ME_450_EMAIL_EXIST) 
            user = serializer.save()
            serializer.send_mail()
            data['message'] = 'Registered successfully! A mail sent to your mailbox for activation account.'
            # data['message'] = 'Registered successfully!'
            group = ""
            try:
                group = request.data.get('group')
            except:
                pass
            data['results'] = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'group': group,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

@api_view(['POST'])
def registration_employer_view(request):
    if request.method == 'POST':
        serializer = RegistrationEmployerSerializer(data=request.data)
        data = {}        
        serializer.validate_custom(request.data)
        if serializer.is_valid():
            check_exist = serializer.is_email_exist()
            if check_exist:
                data['email'] = check_exist
                return Response(data, status=status_http.HTTP_ME_450_EMAIL_EXIST) 
            user = serializer.save()
            serializer.send_mail()
            data['message'] = 'Registered successfully! A mail sent to your mailbox for activation account.'
            # data['message'] = 'Registered successfully!'
            group = ""
            try:
                group = request.data.get('group')
            except:
                pass
            data['results'] = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'group': group,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            data = serializer.validate_custom(request.data)
            # data['message'] = 'Registered successfully! A mail sent to your mailbox for activation account.'
            return Response(data, status=status.HTTP_200_OK)   
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTokenValid])
def logout_view(request):
    if request.method == 'POST':
        data = {}
        try:
            user = request.user
            user.token = None
            user.save()
            data['message'] = 'Successfully logged out.'
            return Response(data, status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)  
    return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)    