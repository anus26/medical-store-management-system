from django.shortcuts import render, redirect

from .models import Medicine, Sale
from .forms import MedicineForm


def home(request):
    return render(request, 'index.html')


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
        total_price = medicine.price * quantity

        # Sale save karo
        Sale.objects.create(
            medicine=medicine,
            quantity=quantity,
            total_price=total_price
        )

        # Invoice page
        return render(request, 'invoice.html', {
            'medicine': medicine,
            'quantity': quantity,
            'total': total_price
        })

    # GET request → form show karo
    return render(request, 'create_sale.html', {'medicines': medicines})