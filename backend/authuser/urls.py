from django.urls import path
from .views import PreRegisterUser, VerifyAndRegisterUser , LoginUser , LogoutView , CurrentUserView
from .views import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('pre-register/', PreRegisterUser.as_view(), name='pre_register'),
    path('verify-register/', VerifyAndRegisterUser.as_view(), name='verify_register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]