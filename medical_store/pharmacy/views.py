


import json
from statistics import quantiles

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum,Q
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Invoice, Medicine, Sale,Purchase,Supplier,Customer

from django.contrib.auth.models import Group,User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import MedicineForm


def home(request):

    if not  request.user.is_authenticated:
     return redirect('login')

    if request.user.groups.filter(name="Admin").exists():
        return redirect('admin_dashboard')
    elif request.user.groups.filter(name="Staff").exists():
        return redirect('staff_dashboard')
    
def user_logout(request):
     logout(request)
     return redirect('login')    
    # medicines=Medicine.objects.all()
    # tablets=Medicine.objects.filter(category='Tablets')
    # syrups=Medicine.objects.filter(category='syrup')
    # purchase=Purchase.objects.all()
    # sales=Sale.objects.all()

    # totalProfit=0
    # for sale in sales:
    #     purchase=Purchase.objects.filter(medicine=sale.medicine).last()
    #     if purchase:
    #         profit=sale.total_price-(purchase.price*sale.quantity)
    #         totalProfit+=profit
    # return render(request, 'index.html',
    #             { 'medicines':medicines,
    #              'tablets':tablets,
    #              'syrups':syrups,
    #              'totalProfit':totalProfit}
    #               )


def add_medicine(request):
    form = MedicineForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('add_medicine')

    return render(request, 'add_medicine.html', {'form': form})






def invoices(request):
    invoices = Invoice.objects.all().order_by('-id')
    current_invoice = invoices.first()   # 👈 latest invoice

    return render(request, 'invoices.html', {
        'invoices': invoices,
        'current_invoice': current_invoice
    })

def create_sale(request):
    medicines = Medicine.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        medicine_ids = request.POST.getlist('medicine')
        quantities = request.POST.getlist('quantity')
        customer_id = request.POST.get('customer')

        if not customer_id:
            return render(request, 'create_sale.html', {
                'medicines': medicines,
                'customers': customers,
                'error': "Customer required"
            })

        customer = Customer.objects.get(id=customer_id)

        subtotal = 0   # ✅ FIXED
        sale_items = []

        for med_id, qty in zip(medicine_ids, quantities):

            if not qty:
                continue

            qty = int(qty)
            medicine = Medicine.objects.get(id=med_id)

            if qty > medicine.quantity:
                return render(request, 'create_sale.html', {
                    'medicines': medicines,
                    'customers': customers,
                    'error': f"{medicine.name} out of stock"
                })

            total_price = medicine.price * qty
            subtotal += total_price

            sale_items.append({
                'medicine': medicine,
                'quantity': qty,
                'total_price': total_price
            })

        if not sale_items:
            return render(request, 'create_sale.html', {
                'error': "No items selected",
                'medicines': medicines,
                'customers': customers
            })

        tax = subtotal * 0.10
        total = subtotal + tax

        with transaction.atomic():

            invoice = Invoice.objects.create(
                customer=customer,
                subtotal=subtotal,
                tax=tax,
                total=total
            )

            for item in sale_items:   # ✅ FIXED
                Sale.objects.create(
                    invoice=invoice,
                    medicine=item['medicine'],
                    customer=customer,
                    quantity=item['quantity'],
                    total_price=item['total_price']
                )

                # ✅ stock update inside loop
                item['medicine'].quantity -= item['quantity']
                item['medicine'].save()

        return redirect('invoices')

    return render(request, 'create_sale.html', {
        'medicines': medicines,
        'customers': customers
    })

def purchase_invoice(request):
    purchases = Purchase.objects.all().order_by('-id')
    current_purchase = purchases.first()

    for p in purchases:
        p.total = p.quantity * p.price

    total = sum(p.total for p in purchases)

    return render(request, 'purchase_invoice.html', {
        'purchases': purchases,
        'current_purchase': current_purchase,
        'total': total
    })
def create_purchase(request):
    medicines = Medicine.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        medicine_ids = request.POST.getlist('medicine_id')
        # medicine_name = request.POST.getlist('medicine_name')
        quantites = request.POST.getlist('quantity')
        prices = request.POST.getlist('price')
        supplier_id = request.POST.get('supplier')  # ✅ FIXED
       

        expiry_dates = request.POST.getlist('expiry_date')

        supplier = Supplier.objects.get(id=supplier_id)
        payment_method=request.POST.get('payment_method')
        payment_status=request.POST.get('payment_status')

        total=0
        for med_id,qty,price,exp in zip(medicine_ids,quantites,prices,expiry_dates):
            if not med_id:   # 🔥 IMPORTANT CHECK
                continue

            qty = int(qty)
            price = float(price)

            if med_id:
                medicine = Medicine.objects.get(id=med_id)
            else:
                continue

            Purchase.objects.create(
                medicine=medicine,
                supplier=supplier,
                quantity=qty,
                price=price,
                expiry_date=exp,
                payment_method=payment_method,
                payment_status=payment_status
            )

            # stock update
            medicine.quantity += qty
            medicine.save()
            total += qty * price
   
        return redirect('purchase_invoice')
    
    return render(request, 'create_purchase.html', {
        'medicines': medicines,
        'suppliers': suppliers
    }) 

def supplier_report(request):
    purchase=Purchase.objects.select_related('supplier').all()
    return render(request,'supplier_report.html',{
        'purchase':purchase
    })

    # update medicine
def update_medicine(request, id):
    medicine = Medicine.objects.get(id=id)
    form = MedicineForm(request.POST or None, instance=medicine)

    if form.is_valid():
        form.save()
        return redirect('home')

    return render(request, 'update_medicine.html', {'form': form})

    # delete medicine
def delete_medicine(request, id):
    medicine=Medicine.objects.get(id=id)

    if request.method=='POST':
        medicine.delete()
        return redirect('home')

    return render(request,'delete_medicine.html',{'medicine':medicine})

def profit(request,id):
    medicine=Medicine.objects.get(id=id)
    purchase=Purchase.objects.filter(medicine=medicine).last()
    sale=Sale.objects.filter(medicine=medicine).last()

    if purchase and sale:
        profit=sale.total_price-(purchase.price * sale.quantity)
    else:
        profit=0

    return render(request,'profit.html',{
        'medicine':medicine,
        'profit':profit
    })



def supplier(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        companyname = request.POST.get('companyname')
        address = request.POST.get('address')

        # Save to database
        Supplier.objects.create(
            name=name,
            email=email,
            contact=contact,
            companyname=companyname,
            address=address
        )

        return redirect('supplier')  # page refresh

    return render(request, 'supplier.html')



def supplier_report(request):
    purchase=Purchase.objects.select_related('supplier').all()
    return render(request,'supplier_report.html',{
        'purchase':purchase
    })


def add_customer(request):
    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')

        Customer.objects.create(
            name=name,
            contact=contact,
            address=address
        )

        return redirect('customer_list')

    return render(request, 'add_customer.html')



def customer_list(request):
    customers=Customer.objects.all().order_by('-id')
    return render(request,'customer_list.html',{
        'customers':customers
    })


def customer_history(request, id):
    customer = Customer.objects.get(id=id)
    sales = Sale.objects.filter(customer=customer)

    return render(request, 'customer_history.html', {
        'customer': customer,
        'sales': sales
    })

def delete_customer(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    return redirect('customer_list')   # ✅ always return
    

def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        group_name = request.POST.get('group')   

        # ✅ user ko variable me store karo
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # ✅ group assign karo
        group_name = request.POST.get('group')

        group_obj, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group_obj)

        return redirect('login')

    return render(request, 'add_user.html')    



def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ DEBUG (optional)
            print(user.groups.all())

            # ✅ ROLE BASED REDIRECT
            if user.groups.filter(name="Admin").exists():
                return redirect("admin_dashboard")

            elif user.groups.filter(name="Staff").exists():
                return redirect("staff_dashboard")

            else:
                return redirect("login")  # fallback

        else:
            return render(request, "login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "login.html")





@login_required
def admin_dashboard(request):

    # ✅ ROLE FLAGS (FIXED)
    is_admin = request.user.groups.filter(name="Admin").exists()
    is_staff = request.user.groups.filter(name="Staff").exists()

    # ❌ ACCESS CONTROL
    if not is_admin:
        return redirect("login")

    medicines = Medicine.objects.all()

    # 📊 Monthly Sales
    monthly_sales = (
        Sale.objects
        .annotate(month=ExtractMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_price'))
        .order_by('month')
    )

    months = [0] * 12

    for item in monthly_sales:
        idx = item['month'] - 1
        months[idx] = item['total'] or 0

    # 💰 TOTALS
    sales = Sale.objects.all()
    purchases = Purchase.objects.all()

    total_sales = sum(s.total_price or 0 for s in sales)
    total_purchase = sum(p.quantity * p.price for p in purchases)
    profit = total_sales - total_purchase

    return render(request, "admin_dashboard.html", {
        "medicines": medicines,
        "total_sales": total_sales,
        "total_purchase": total_purchase,
        "profit": profit,
        "monthly_sales": json.dumps(months),

        # ✅ sidebar control
        "is_admin": is_admin,
        "is_staff": is_staff,
    })

@login_required
def staff_dashboard(request):

    is_admin = request.user.groups.filter(name="Admin").exists()
    is_staff = request.user.groups.filter(name="Staff").exists()

    if not is_staff and not is_admin:
        return redirect("login")

    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    sales_list = Sale.objects.select_related('medicine', 'customer').all().order_by('-id')

    # 🔍 SEARCH FIX
    if search_query:
        sales_list = sales_list.filter(
            Q(medicine__name__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    # 📅 DATE FILTER
    if date_from:
        sales_list = sales_list.filter(created_at__gte=date_from)

    if date_to:
        sales_list = sales_list.filter(created_at__lte=date_to)

    # 📄 PAGINATION
    paginator = Paginator(sales_list, 5)
    page = request.GET.get('page')
    sales = paginator.get_page(page)

    return render(request, "staff_dashboard.html", {
        "sales": sales,
        "search_query": search_query,
        "date_from": date_from,
        "date_to": date_to,

        # sidebar fix
        "is_admin": is_admin,
        "is_staff": is_staff,
    })












# @login_required
# def staff_dashboard(request):

#     search_query = request.GET.get('search', '')
#     date_from = request.GET.get('date_from')
#     date_to = request.GET.get('date_to')

#     sales_list = Sale.objects.select_related('medicine', 'customer').all().order_by('-id')

#     # 🔍 SEARCH
#     if search_query:
#         sales_list = sales_list.filter(
#             Q(medicine__name__icontains=search_query) |
#             Q(customer__name__icontains=search_query)
#         )

#     # 📅 DATE FILTER
#     if date_from:
#         sales_list = sales_list.filter(data__gte=date_from)

#     if date_to:
#         sales_list = sales_list.filter(data__lte=date_to)

#     # 📄 PAGINATION
#     paginator = Paginator(sales_list, 5)
#     page = request.GET.get('page')
#     sales = paginator.get_page(page)

#     # 🔥 AJAX REQUEST (LIVE SEARCH)
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('partials/sale_table.html', {'sales': sales})
#         return JsonResponse({'html': html})

#     return render(request, "staff_dashboard.html", {
#         'sales': sales,
#         'search_query': search_query,
#         'date_from': date_from,
#         'date_to': date_to
#     })