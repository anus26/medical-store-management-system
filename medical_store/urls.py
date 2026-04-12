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

from pharmacy.views import home, user_logout

from django.contrib import admin
from django.urls import path


from pharmacy.views import add_customer, add_user, customer_history, customer_list, delete_customer, delete_medicine, invoices, create_sale, create_purchase, home, add_medicine, user_login,purchase_invoice, supplier, update_medicine, profit, admin_dashboard,  staff_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='home'),
    path('add_medicine/', add_medicine, name='add_medicine'),
    path('invoices/', invoices, name='invoices'),
    path('create_sale/', create_sale, name='create_sale'),
    path('create_purchase/',create_purchase, name='create_purchase'),
    path('purchase_invoice/',purchase_invoice, name='purchase_invoice'),
    path('update_medicine/<int:id>/',update_medicine,name='update_medicine'),
    path('delete_medicine/<int:id>/',delete_medicine,name='delete_medicine'),
    path('profit/<int:id>/',profit,name='profit' ),
    path('supplier/',supplier ,name='supplier'),
    path('add_customer/',add_customer ,name='add_customer'),
   path('customer_list/',customer_list, name='customer_list'),
   path('customer-history/<int:id>/', customer_history, name='customer_history'),
     path('delete_customer/<int:id>/',delete_customer, name='delete_customer'),
     path('add_user/', add_user, name='add_user'),
    path('login/',user_login, name="login"),
    path("admin_dashboard/",admin_dashboard, name='admin_dashboard'),
    path("staff_dashboard/",staff_dashboard, name='staff_dashboard'),
    path('logout/', user_logout, name='logout')
]
