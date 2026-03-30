from django.db import models

class Medicine(models.Model):
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    price=models.FloatField()
    quantity=models.IntegerField()
    expiry_date=models.DateField()

    def __str__(self):
        return self.name
    
class Purchase(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.medicine.name  

class Supplier(models.Model):
    name=models.CharField(max_length=100)
    contact=models.CharField(max_length=20)
    address=models.TextField()
    def __str__(self):
        return self.name
    
class Sale(models.Model):
    medicine=models.ForeignKey(Medicine,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    total_price=models.FloatField()
    data=models.DateField(auto_now_add=True)    
    def save(self,*args,**kwargs):
        self.total_price=self.medicine.price*self.quantity
        self.medicine.quantity-=self.quantity
        self.medicine.save()
        super().save(*args,**kwargs)