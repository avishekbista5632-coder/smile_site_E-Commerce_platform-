from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.signup_view, name='signin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),
    path('thankyou/', views.thankyou_view, name='thankyou'),
    path('checkout/', views.checkout, name='checkout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path("reset-password/<uidb64>/<token>/", views.reset_password_view, name="reset_password"),
    path("email-verified/", views.email_verified_success, name="email_verified_success"),
    path("password-reset-sent/", views.password_reset_sent, name="password_reset_sent"),
    path('api/check-verification', views.check_verification, name='check_verification_api'),
]
