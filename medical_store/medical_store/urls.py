# """
# URL configuration for medical_store project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """

from django.contrib import admin
from django.urls import path
from pharmacy.views import invoices,create_sale,create_purchase, home,add_medicine

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='home'),
    path('add_medicine/', add_medicine, name='add_medicine'),
    path('create_sale/', create_sale, name='create_sale'),
    path('invoices/', invoices, name='invoices'),
    path('create_purchase/',create_purchase, name='create_purchase')
    
]
