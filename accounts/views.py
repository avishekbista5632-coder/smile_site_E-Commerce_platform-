from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db import transaction  # ✅ Needed for atomic()
from django.core.mail import EmailMessage,EmailMultiAlternatives  # ✅ Needed for sending emails
import json
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import never_cache

# Models
from shop.models import Product, Order, OrderItem  # ✅ Your models


def check_verification(request):
    email = request.GET.get("email")
    try:
        user = User.objects.get(email=email)
        return JsonResponse({"verified": user.is_active})
    except User.DoesNotExist:
        return JsonResponse({"verified": False})
# --- FORGOT PASSWORD ---
def forgot_password_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or "/"

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse("reset_password", kwargs={"uidb64": uid, "token": token})
            )

            # Render HTML email content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #fff; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <p style="color:#555;">Hi {user.first_name}, we received a request to reset your password.</p>
                    <a href="{reset_url}" style="display:inline-block; padding:14px 30px; background-color:#4CAF50; color:#fff; text-decoration:none; border-radius:8px; font-weight:600; font-size:16px;">Reset Password</a>
                    <p style="margin-top:20px; color:#999;">If you did not request this, you can ignore this email.</p>
                </div>
            </body>
            </html>
            """

            text_content = f"Hi {user.first_name},\n\nReset your password using this link: {reset_url}\n\nIgnore if you didn't request this."

            # Send email
            email_msg = EmailMultiAlternatives(
                subject="Password Reset Request",
                body=text_content,
                from_email="avishekbista5632@gmail.com",
                to=[user.email],
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            messages.success(request, "Password reset link sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")

        # Redirect to password_reset_sent page
        return redirect(f"{reverse('password_reset_sent')}?next={next_url}")

    # GET request → show form
    return render(request, "shop/forgot_password.html", {"next": next_url})



# --- password_reset_sent ---
def password_reset_sent(request):
    return render(request, "shop/password_reset_sent.html")



# --- reset PASSWORD ---

@never_cache
def reset_password_view(request, uidb64, token):
    password_reset_done = False

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired reset link.")
        return redirect("forgot_password")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif not password1:
            messages.error(request, "Password cannot be empty.")
        else:
            user.set_password(password1)
            user.save()
            messages.success(
                request,
                "Your password has been reset successfully. Please return to the previous tab to log in."
            )
            password_reset_done = True

    return render(
        request,
        "shop/reset_password.html",
        {"password_reset_done": password_reset_done}
    )

# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or "/"

        if not name or not email or not password:
            return render(request, 'shop/signin.html', {
                "error": "All fields are required.",
                "next": next_url
            })

        if User.objects.filter(username=email).exists():
            login_url = f"{reverse('login')}?next={next_url}"
            messages.info(request, "Email already registered. Please login.")
            return redirect(login_url)

        # 🔒 Create inactive user
        user = User.objects.create_user(
            username=email,
            first_name=name,
            email=email,
            password=password,
            is_active=False
        )

        # 🔑 Generate verification link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        protocol = "http"  # force HTTP in dev
        domain = request.get_host()  # includes port
        verify_url = f"{protocol}://{domain}/verify/{uid}/{token}/"

        # 📧 Send verification email
        html_message = render_to_string(
            "shop/email_verify.html",
            {"user": user, "verify_url": verify_url}
        )

        email_message = EmailMessage(
            subject="Verify Your Email — Smile Cleaning Products",
            body=html_message,
            to=[email]
        )
        email_message.content_subtype = "html"
        email_message.send(fail_silently=True)

        # 🔁 Redirect to login WITH next preserved
        messages.success(
            request,
            "Account created! Please verify your email before logging in."
        )
        return redirect(f"{reverse('login')}?next={next_url}")

    next_url = request.GET.get('next', '/')
    return render(request, 'shop/signin.html', {"next": next_url})


# ---------------- LOGIN ----------------
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            return render(request, 'shop/login.html', {"error": "Both fields are required.", "next": next_url})

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            if not user.is_active:
                return render(request, 'shop/login.html', {"error": "Please verify your email before logging in.", "next": next_url})

            login(request, user)
            return redirect(next_url)  # Redirect back to original page

        return render(request, 'shop/login.html', {"error": "Invalid email or password.", "next": next_url})

    return render(request, 'shop/login.html', {"next": next_url})

# ---------------- verify_email_view ----------------
def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # 🔑 REDIRECT — DO NOT render here
        return redirect("email_verified_success")

    messages.error(request, "Verification link is invalid or expired.")
    return redirect("login")


# ---------------- email_verified_success ----------------
def email_verified_success(request):
    return render(request, "shop/email_verified_success.html")

# ---------------- THANK YOU ----------------
def thankyou_view(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    if not request.user.is_authenticated or (order.user and order.user != request.user):
        return redirect(f'/signin/?next=/checkout/')
    return render(request, 'shop/thankyou.html', {'order': order})

# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("/")



# CHECKOUT VIEW
# -------------------------------
@csrf_exempt
def checkout(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)

        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        contact = data.get("contact", "").strip()
        address = data.get("address", "").strip()
        payment_method = data.get("payment_method", "").strip()
        cart_items = data.get("cart", [])

        if not all([full_name, email, contact, address, payment_method, cart_items]):
            return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

        user = request.user if request.user.is_authenticated else None

        # Fetch products in bulk to reduce DB hits
        product_ids = [item["id"] for item in cart_items]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        total_amount = 0
        for item in cart_items:
            product = products.get(item["id"])
            if not product:
                return JsonResponse({"status": "error", "message": f"Product ID {item['id']} not found"}, status=400)
            total_amount += product.price * int(item["quantity"])

        # Save order + items atomically
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                contact=contact,
                address=address,
                payment_method=payment_method,
                total_amount=total_amount
            )

            order_items = [
                OrderItem(
                    order=order,
                    product=products[item["id"]],
                    quantity=item["quantity"],
                    price_at_purchase=products[item["id"]].price
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

        # ---------------- HTML EMAIL ----------------

        # Render HTML email using a separate template
        current_site = get_current_site(request)  # e.g., example.com
        domain = f"https://{current_site.domain}"  # full absolute URL

        email_html_content = render_to_string('shop/thankyou_email.html', {'order': order,'domain': domain })
        email_text_content = strip_tags(email_html_content)  # fallback plain text

        # Customer email
        customer_email = EmailMessage(
            subject="Order Confirmation — Smile Cleaning Products",
            body=email_html_content,
            to=[email]
        )
        customer_email.content_subtype = "html"  # Important
        customer_email.send(fail_silently=True)

        # Seller email
        seller_email_address = "avishekbista5632@gmail.com"
        seller_email = EmailMessage(
            subject="New Order Received — Smile Cleaning Products",
            body=email_html_content,
            to=[seller_email_address]
        )
        seller_email.content_subtype = "html"
        seller_email.send(fail_silently=True)

        return JsonResponse({
            "status": "success",
            "order_id": order.id,
            "redirect_url": f"/thankyou/?order_id={order.id}"
        })

    except Exception as e:
        print("Checkout error:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
