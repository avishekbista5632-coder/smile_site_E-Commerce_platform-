import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.mail import EmailMessage, BadHeaderError
from django.db import transaction
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Product, Order, OrderItem


# -------------------------------
# PAGE VIEWS (HTML pages)
# -------------------------------

def home(request):
    products = Product.objects.prefetch_related('gallery').all()
    return render(request, 'shop/home.html', {'products': products})

def product_list(request):
    products = Product.objects.prefetch_related('gallery').all()
    return render(request, 'shop/product.html', {'products': products})

def product_detail(request, id):
    """
    Display product detail page.
    JS will handle finding the correct product from the products list using `product_id`.
    """
    products = Product.objects.prefetch_related('gallery').all()
    return render(request, 'shop/product-detail.html', {
        'products': products,
        'product_id': id
    })

def aboutus(request):
    return render(request, 'shop/aboutus.html')

def contactus(request):
    return render(request, 'shop/contactus.html')

def cart(request):
    return render(request, 'shop/carticon.html')

def signin(request):
    return render(request, 'shop/signin.html')

def login_view(request):
    return render(request, 'shop/login.html')

# -------------------------------
# CONTACT FORM EMAIL VIEW
# -------------------------------

def send_message(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            email_msg = EmailMessage(
                subject="New Contact Form Message",
                body=full_message,
                from_email='avishekbista5632@gmail.com',  # your email
                to=['avishekbista5632@gmail.com'],        # recipient
                reply_to=[email]                           # visitor's email
            )
            email_msg.send(fail_silently=False)
            messages.success(request, "Your message has been sent successfully!")
        except BadHeaderError:
            messages.error(request, "Invalid header found. Message not sent.")
        except Exception as e:
            messages.error(request, f"Error sending message: {e}")

        return redirect('contactus')

    messages.error(request, "Invalid request. Please try again.")
    return redirect('contactus')


# # -------------------------------
# # CHECKOUT VIEW
# # -------------------------------

# @csrf_exempt
# def checkout(request):
#     if request.method != "POST":
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

#     try:
#         data = json.loads(request.body)

#         full_name = data.get("full_name", "").strip()
#         email = data.get("email", "").strip()
#         contact = data.get("contact", "").strip()
#         address = data.get("address", "").strip()
#         payment_method = data.get("payment_method", "").strip()
#         cart_items = data.get("cart", [])

#         if not all([full_name, email, contact, address, payment_method, cart_items]):
#             return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

#         user = request.user if request.user.is_authenticated else None

#         # ---- Fetch products in bulk to reduce DB hits ----
#         product_ids = [item["id"] for item in cart_items]
#         products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

#         total_amount = 0
#         for item in cart_items:
#             product = products.get(item["id"])
#             if not product:
#                 return JsonResponse({"status": "error", "message": f"Product ID {item['id']} not found"}, status=400)
#             total_amount += product.price * int(item["quantity"])

#         # ---- Save order + items atomically ----
#         with transaction.atomic():
#             order = Order.objects.create(
#                 user=user,
#                 full_name=full_name,
#                 email=email,
#                 contact=contact,
#                 address=address,
#                 payment_method=payment_method,
#                 total_amount=total_amount
#             )

#             order_items = [
#                 OrderItem(
#                     order=order,
#                     product=products[item["id"]],
#                     quantity=item["quantity"],
#                     price_at_purchase=products[item["id"]].price
#                 )
#                 for item in cart_items
#             ]
#             OrderItem.objects.bulk_create(order_items)  # faster bulk insert

#         # ---- Prepare email content ----
#         items_text = "\n".join([
#             f"{products[i['id']].name} x {i['quantity']} — Rs. {products[i['id']].price}" for i in cart_items
#         ])

#         # Email to seller
#         seller_email = "avishekbista5632@gmail.com"
#         EmailMessage(
#             subject="New Order Received — Smile Cleaning Products",
#             body=f"""
# Hello,

# You have received a new order.

# Customer: {full_name}
# Email: {email}
# Contact: {contact}
# Address: {address}
# Payment Method: {payment_method}

# Items Ordered:
# {items_text}

# Total Amount: Rs. {total_amount}

# Thank you,
# Smile Cleaning Products
# """,
#             to=[seller_email]
#         ).send(fail_silently=True)

#         # Email to customer
#         EmailMessage(
#             subject="Order Confirmation — Smile Cleaning Products",
#             body=f"""
# Hello {full_name.split()[0]},

# Thank you for your order!

# Order Summary:
# {items_text}

# Total Amount: Rs. {total_amount}
# Shipping Address:
# {address}

# Payment Method: {payment_method}

# We will contact you soon regarding delivery.

# Smile Cleaning Products Team
# """,
#             to=[email]
#         ).send(fail_silently=True)

#         return JsonResponse({"status": "success", "order_id": order.id, "redirect_url": "/thankyou/"})

#     except Exception as e:
#         print("Checkout error:", e)
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)


# -------------------------------
# THANK YOU PAGE
# -------------------------------
def thankyou_view(request):
    return render(request, 'shop/thankyou.html')
