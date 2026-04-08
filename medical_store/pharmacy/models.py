from django.db import models


class Supplier(models.Model):
    name=models.CharField(max_length=100)
    contact=models.CharField(max_length=20)
    address=models.TextField()
    companyname=models.CharField(max_length=150)
    email=models.EmailField()
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    price=models.FloatField()
    quantity=models.IntegerField()
    supplier=models.ForeignKey(Supplier, on_delete=models.CASCADE)
    expiry_date=models.DateField()

    def __str__(self):
        return self.name
    
class Purchase(models.Model):
    PAYMENT_METHODS={
        ('cash','Cash'),
        ('card','Card'),
        ('online','Online')
    }
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    supplier=models.ForeignKey(Supplier,on_delete=models.CASCADE)
    expiry_date = models.DateField()
    payment_method=models.CharField(max_length=20,choices=PAYMENT_METHODS)
    payment_status=models.CharField(max_length=20,default='paid')

    date=models.DateTimeField(auto_now_add=True)
    def save(self,*args,**kwargs):
     self.total_price=self.price*self.quantity
     self.medicine.quantity+=self.quantity
     self.medicine.save()
     super().save(*args,**kwargs)
    def __str__(self):
        return self.medicine.name  
class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    
    
class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    subtotal=models.FloatField(default=0)
    tax=models.FloatField(default=0)
    total=models.FloatField(default=0)
class Sale(models.Model):
    invoice=models.ForeignKey(Invoice,on_delete=models.CASCADE,related_name='items')
    medicine=models.ForeignKey(Medicine,on_delete=models.CASCADE)
    customer=models.ForeignKey('Customer',on_delete=models.CASCADE)
    quantity=models.IntegerField()
    total_price=models.FloatField()
    data=models.DateField(auto_now_add=True)    
    def save(self,*args,**kwargs):
        self.total_price=self.medicine.price*self.quantity
        self.medicine.quantity-=self.quantity
        self.medicine.save()
        super().save(*args,**kwargs)




