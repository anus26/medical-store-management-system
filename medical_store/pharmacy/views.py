


from django.shortcuts import render, redirect

from .models import Medicine, Sale,Purchase,Supplier,Customer

from django.contrib.auth.models import Group,User
from django.contrib.auth import authenticate, login

from .forms import MedicineForm


def home(request):
    medicines=Medicine.objects.all()
    tablets=Medicine.objects.filter(category='Tablets')
    syrups=Medicine.objects.filter(category='syrup')
    purchase=Purchase.objects.all()
    sales=Sale.objects.all()

    totalProfit=0
    for sale in sales:
        purchase=Purchase.objects.filter(medicine=sale.medicine).last()
        if purchase:
            profit=sale.total_price-(purchase.price*sale.quantity)
            totalProfit+=profit
    return render(request, 'index.html',
                { 'medicines':medicines,
                 'tablets':tablets,
                 'syrups':syrups,
                 'totalProfit':totalProfit}
                  )


def add_medicine(request):
    form = MedicineForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('add_medicine')

    return render(request, 'add_medicine.html', {'form': form})

def create_sale(request):
    medicines = Medicine.objects.all()   # 👈 sab medicines fetch karo

    if request.method == "POST":
        medicine_id = request.POST.get('medicine')
        quantity = int(request.POST.get('quantity'))

        medicine = Medicine.objects.get(id=medicine_id)
        if quantity > medicine.quantity:
            return render(request, 'create_sale.html', {
                'medicines': medicines,
                'error': "Not enough stock!"
            })

        total_price = medicine.price * quantity

        # ✅ STOCK DECREASE
        medicine.quantity -= quantity
        medicine.save()
        customer_id = request.POST.get('customer')
        customer = Customer.objects.get(id=customer_id)

        # Sale save karo
        Sale.objects.create(
            medicine=medicine,
            customer=customer,
            quantity=quantity,
            total_price=total_price
        )

        # Invoice page
        return render(request, 'invoices.html', {
            'medicine': medicine,
            'quantity': quantity,
            'total': total_price
        })

    # GET request → form show karo
    return render(request, 'create_sale.html', {'medicines': medicines})
def invoices(request):
    sales = Sale.objects.all()
    return render(request, 'invoices.html', {'sales': sales})



def create_purchase(request):
    medicines = Medicine.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        medicine_id = request.POST.get('medicine_id')
        medicine_name = request.POST.get('medicine_name')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        supplier_id = request.POST.get('supplier')  # ✅ FIXED
        expiry_date = request.POST.get('expiry_date')
        if not quantity or not price or not supplier_id:
            return render(request, 'create_purchase.html', {
                'medicines': medicines,
                'suppliers': suppliers,
                'error': 'All fields required'
            })

        quantity = int(quantity)
        price = float(price)

        supplier = Supplier.objects.get(id=supplier_id)

        if medicine_id:
            medicine = Medicine.objects.get(id=medicine_id)

        elif medicine_name:
            medicine = Medicine.objects.create(
                name=medicine_name,
                quantity=0,
                price=price,
                supplier=supplier,
                expiry_date=expiry_date
            )
        else:
            return render(request, 'create_purchase.html', {
                'medicines': medicines,
                'suppliers': suppliers,
                'error': 'Select or enter medicine'
            })
        payment_method=request.POST.get('payment_method')
        payment_status=request.POST.get('payment_status')

        Purchase.objects.create(
            medicine=medicine,
            supplier=supplier,  # ⚠️ ye missing tha
            quantity=quantity,
            price=price,
            expiry_date=expiry_date,
            payment_method=payment_method,
    payment_status=payment_status
        )

        # stock update
        medicine.quantity += quantity
        medicine.save()

        return render(request, 'purchase_invoice.html', {
            'medicine': medicine,
            'quantity': quantity,
            'price': price,
            'total': price * quantity
        })

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





def admin_dashboard(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/login/")
    medicines=Medicine.objects.all()
    tablets=Medicine.objects.filter(category='Tablets')
    syrups=Medicine.objects.filter(category='syrup')
    purchase=Purchase.objects.all()
    sales=Sale.objects.all()

    totalProfit=0
    for sale in sales:
      if purchase:
            profit=sale.total_price-(purchase.price*sale.quantity)
            totalProfit+=profit
    return render(request, "admin_dashboard.html",
           { 'medicines':medicines,
                 'tablets':tablets,
                 'syrups':syrups,
                 'totalProfit':totalProfit}
                  )

def staff_dashboard(request):
    if request.user.groups.filter(name="Staff").exists() or request.user.groups.filter(name="Admin").exists():
        return render(request, "staff_dashboard.html")

    return redirect("/login/")

