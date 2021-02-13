from django.urls import path
from .views import (PasswordReset,
                    PasswordResetDone,
                    PasswordResetConfirm,
                    PasswordResetComplete,
                    UserCreate,
                    UserCreateDone,
                    UserCreateComplete,
                    profile,
                    detail,
                    delete,
                    delete_conf,
                    )
from django.contrib.auth import views as auth_views

app_name = 'user'
urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html',
        next_page='/'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('delete/<username>', delete, name='user_delete'),
    path('delete/confirm/<username>', delete_conf, name='delete_conf'),
    path('register/', UserCreate.as_view(), name='register'),
    path('register/done/', UserCreateDone.as_view(), name='register_done'),
    path('register/complete/<token>/', UserCreateComplete.as_view(), name='register_complete'),
    path('password/reset/', PasswordReset.as_view(), name='reset'),
    path('password/reset/done/', PasswordResetDone.as_view(), name='reset_done'),
    path('password/reset/confirm/<str:uidb64>/<str:token>/', PasswordResetConfirm.as_view(), name='reset_confirm'),
    path('password/reset/complete/', PasswordResetComplete.as_view(), name='reset_complete'),
    path('profile/', profile, name='profile'),
]