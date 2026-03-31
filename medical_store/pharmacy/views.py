from django.shortcuts import render, redirect

from .models import Medicine, Sale,Purchase
from .forms import MedicineForm


def home(request):
    medicines=Medicine.objects.all()
    tablets=Medicine.objects.filter(category='Tablets')
    syrups=Medicine.objects.filter(category='syrup')
    return render(request, 'index.html',
                { 'medicines':medicines,
                 'tablets':tablets,
                 'syrups':syrups}
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

        # Sale save karo
        Sale.objects.create(
            medicine=medicine,
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

    if request.method == "POST":
        medicine_id = request.POST.get('medicine')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')

        # ✅ Validation
        if not medicine_id or not quantity or not price:
            return render(request, 'create_purchase.html', {
                'medicines': medicines,
                'error': 'All fields required'
            })

        quantity = int(quantity)
        price = float(price)

        medicine = Medicine.objects.get(id=medicine_id)

        # ✅ Purchase save
        Purchase.objects.create(
            medicine=medicine,
            quantity=quantity,
            price=price
        )
        # ✅ Stock increase
        medicine.quantity += quantity
        medicine.save()

        return render(request,'purchase_invoice.html', {
            'medicine': medicine,
            'quantity': quantity,
            'price': price,
            'total': price * quantity
    })

    return render(request, 'create_purchase.html', {'medicines': medicines})

    
    # update medicine
def update_medicine(request, id):
    medicine = Medicine.objects.get(id=id)
    form = MedicineForm(request.POST or None, instance=medicine)

    if form.is_valid():
        form.save()
        return redirect('home')

    return render(request, 'update_medicine.html', {'form': form})
