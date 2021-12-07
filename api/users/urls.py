
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .serializers import MySimpleJWTSerializer, MyTokenObtainPairView
from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # # settings
    # path('settings/change-password/', change_password_view),
    # path('settings/change-email/', change_email_view),
    # # user
    # # path('account/get-group-with-permission/', get_group_with_permission_view),
    # path('account/get-user-profile/', get_profile_view),
    # path('account/update-user-profile/', update_user_profile_view),
    path('account/get-user-info/', get_user_info_view),
    # auth
    # url(r'^auth/login/$', MyTokenObtainPairView.as_view()),
    url(r'^auth/login/$', login_view),
    path('auth/logout/', logout_view),
    path('auth/sign-up/', registration_view),    
    path('auth/sign-up/employer/', registration_employer_view),    
    path('auth/forgot-password/', forgot_password_view),
    path('auth/resend-link-active/', resend_link_activation_view),
    path('auth/active-account/', active_account_view),
    path('auth/create-access-token/', create_access_token_view),
    path('auth/reset-password/', reset_password_view),
    # other module
    # path('', include('api.searches.urls')), # searches
]