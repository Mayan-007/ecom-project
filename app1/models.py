from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='category/')

    def __str__(self):
        return self.name
    
class Product(models.Model):
    vendor_id = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='product/')
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_desc = models.TextField()
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    message = models.TextField()
    
    def __str__(self):
        return self.name
    
class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    user_phone = models.CharField(max_length=100)
    shipping_address = models.TextField()
    order_amount = models.IntegerField()
    payment_method = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user_id.name
    
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_qty = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    cart_amount = models.IntegerField()
    cart_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.product_id.name