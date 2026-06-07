from django.db import models

class Shoe(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # NEW: The crossed-out price! We allow it to be blank in case a shoe isn't on sale.
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='shoe_images/', blank=True, null=True) # The Main Display Image

    def str(self):
        return self.name

class ShoeSize(models.Model):
    shoe = models.ForeignKey(Shoe, related_name='sizes', on_delete=models.CASCADE)
    size_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)

    def str(self):
        status = "Available" if self.is_available else "Out of Stock"
        return f"Size {self.size_number} - {status}"

# --- NEW: The Multi-Image Gallery ---
class ShoeImage(models.Model):
    shoe = models.ForeignKey(Shoe, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shoe_images/gallery/')

    def str(self):
        return f"Gallery image for {self.shoe.name}"

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    delivery_address = models.CharField(max_length=255)
    shoe = models.ForeignKey(Shoe, on_delete=models.SET_NULL, null=True, blank=True)
    shoe_size = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Order {self.id} - {self.customer_name}"