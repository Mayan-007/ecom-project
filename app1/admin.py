from django.contrib import admin
from app1.models import *
    
class categoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'img')
    list_filter = ('name', 'img')
    search_fields = ('name', 'img')
    
class productAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'product_desc')
    list_filter = ('name', 'price', 'category', 'product_desc')
    search_fields = ('name', 'price', 'category', 'product_desc')
    
class userAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password', 'address', 'phone')
    list_filter = ('name', 'email', 'password', 'address', 'phone')
    search_fields = ('name', 'email', 'password', 'address', 'phone')
    
class contactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    list_filter = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')
    
class orderAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'order_amount')
    list_filter = ('user_id', 'order_amount')
    search_fields = ('user_id', 'order_amount')
    
class vendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password', 'address', 'phone')
    list_filter = ('name', 'email', 'password', 'address', 'phone')
    search_fields = ('name', 'email', 'password', 'address', 'phone')
    
class cartAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_qty', 'user_id', 'cart_amount')
    list_filter = ('product_id', 'product_qty', 'user_id', 'cart_amount')
    search_fields = ('product_id', 'product_qty', 'user_id', 'cart_amount')

admin.site.register(Category, categoryAdmin)
admin.site.register(Product, productAdmin)
admin.site.register(User, userAdmin)
admin.site.register(Contact, contactAdmin)
admin.site.register(Order, orderAdmin)
admin.site.register(Vendor, vendorAdmin)
admin.site.register(Cart, cartAdmin)