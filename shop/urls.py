from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product-list'),
    path('products/<int:id>/', views.product_detail, name='product-detail'),
    path('about/', views.aboutus, name='aboutus'),
    path('contact/', views.contactus, name='contactus'),
    path('cart/', views.cart, name='cart'),
    path('send-message/', views.send_message, name='send_message'),
]
