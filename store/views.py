import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .mpesa import trigger_stk_push
from .models import Order, Shoe

def store_home(request):
    all_shoes = Shoe.objects.all()
    return render(request, 'store/index.html', {'shoes': all_shoes})

# --- CART FUNCTIONS ---
def add_to_cart(request, shoe_id):
    if request.method == 'POST':
        size = request.POST.get('size')
        if not size:
            return redirect('home')
            
        cart = request.session.get('cart', {})
        # Create a unique tag for the cart: e.g., "1_42" (Shoe ID 1, Size 42)
        item_key = f"{shoe_id}_{size}"
        
        if item_key in cart:
            cart[item_key] += 1
        else:
            cart[item_key] = 1
            
        request.session['cart'] = cart
    return redirect('home')

def remove_from_cart(request, item_key):
    cart = request.session.get('cart', {})
    if item_key in cart:
        del cart[item_key]
    request.session['cart'] = cart
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0
    
    for item_key, quantity in cart.items():
        try:
            shoe_id_str, size = item_key.split('_')
            shoe = Shoe.objects.get(id=int(shoe_id_str))
            subtotal = int(shoe.price) * quantity
            cart_total += subtotal
            
            cart_items.append({
                'item_key': item_key,
                'shoe': shoe,
                'size': size,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except (Shoe.DoesNotExist, ValueError):
            pass # Ignores old cart items without sizes
            
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'cart_total': cart_total})

# --- CHECKOUT FUNCTIONS ---

def checkout(request, shoe_id):
    shoe = Shoe.objects.get(id=shoe_id)
    
    if request.method == "POST":
        size = request.POST.get('size')
        customer_name = request.POST.get('customer_name')
        
        # Scenario A: They just clicked "Buy Now" on the storefront.
        # We have their size, but not their name yet. Send them to the form!
        if size and not customer_name:
            return render(request, 'store/checkout.html', {'shoe': shoe, 'selected_size': size})
            
        # Scenario B: They filled out the checkout form and hit Pay.
        if customer_name and size:
            delivery_address = request.POST.get('delivery_address')
            phone_number = request.POST.get('phone_number')
            amount = int(shoe.price) 
            
            response_data = trigger_stk_push(phone_number, amount)
            
            if response_data and response_data.get("ResponseCode") == "0":
                checkout_id = response_data.get("CheckoutRequestID")
                
                Order.objects.create(
                    customer_name=customer_name,
                    delivery_address=delivery_address,
                    shoe=shoe, 
                    shoe_size=size, # <-- Saves the exact size to the Admin Dashboard!
                    phone_number=phone_number,
                    amount=amount,
                    checkout_request_id=checkout_id,
                    status='Pending'
                )
                return redirect('success')
            else:
                return HttpResponse("<h2>Failed to initiate payment. Try again.</h2>")
                
    # If they try to bypass the size selection by typing the URL manually, send them back
    return redirect('home')

def cart_checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    cart_total = 0
    order_summary = ""
    
    for item_key, quantity in cart.items():
        try:
            shoe_id_str, size = item_key.split('_')
            shoe = Shoe.objects.get(id=int(shoe_id_str))
            cart_total += int(shoe.price) * quantity
            # This creates a text list of everything they bought!
            order_summary += f"{shoe.name} (Sz {size}) x{quantity}, "
        except (Shoe.DoesNotExist, ValueError):
            pass

    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        delivery_address = request.POST.get('delivery_address')
        phone_number = request.POST.get('phone_number')
        
        response_data = trigger_stk_push(phone_number, cart_total)
        
        if response_data and response_data.get("ResponseCode") == "0":
            checkout_id = response_data.get("CheckoutRequestID")
            
            # Attach the exact shoes and sizes to the customer name in the dashboard!
            final_details = f"{customer_name} [{order_summary}]"
            
            Order.objects.create(
                customer_name=final_details[:100], 
                delivery_address=delivery_address,
                shoe=None, 
                phone_number=phone_number,
                amount=cart_total,
                checkout_request_id=checkout_id,
                status='Pending'
            )
            
            request.session['cart'] = {}
            return redirect('success')
        else:
            return HttpResponse("<h2>Failed to initiate payment. Try again.</h2>")

    return render(request, 'store/cart_checkout.html', {'cart_total': cart_total})

def success_page(request):
    return render(request, 'store/success.html')

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        payment_data = json.loads(request.body)
        stk_callback = payment_data['Body']['stkCallback']
        result_code = stk_callback['ResultCode']
        checkout_id = stk_callback['CheckoutRequestID']
        
        try:
            order = Order.objects.get(checkout_request_id=checkout_id)
            if result_code == 0:
                metadata_items = stk_callback['CallbackMetadata']['Item']
                receipt_number = None
                for item in metadata_items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        receipt_number = item.get('Value')
                        break
                
                order.mpesa_receipt = receipt_number
                order.status = 'Paid'
                order.save()
            else:
                order.status = 'Failed'
                order.save()
        except Order.DoesNotExist:
            pass

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"Error": "Only POST requests allowed"})