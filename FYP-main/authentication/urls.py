# authentication/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'  # ADD THIS LINE

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html',
             success_url='/auth/reset/done/'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('switch-role/', views.switch_role_view, name='switch_role'),
]