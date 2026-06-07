from django.contrib import admin
from .models import Order, Shoe, ShoeSize, ShoeImage

class ShoeSizeInline(admin.TabularInline):
    model = ShoeSize
    extra = 4

# NEW: Tells the dashboard to add extra image upload slots!
class ShoeImageInline(admin.TabularInline):
    model = ShoeImage
    extra = 3 

@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'old_price') # Now shows old price in the table!
    inlines = [ShoeSizeInline, ShoeImageInline] # Adds both sizes AND gallery images to the page

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone_number', 'shoe', 'shoe_size', 'delivery_address', 'status', 'created_at')
    list_filter = ('status', 'created_at')