from django.shortcuts import render, redirect, get_object_or_404
from .models import *

from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# ================= HOME =================
def home(request):

    products = Product.objects.all()

    categories = Category.objects.all()

    banners = Banner.objects.filter(active=True)

    q = request.GET.get("q")
    category = request.GET.get("category")

    if q:
        products = products.filter(name__icontains=q)

    if category:
        products = products.filter(category_id=category)

    return render(request, "shop/home.html", {
        "products": products,
        "categories": categories,
        "banners": banners,
        "selected_category": category
    })


# ================= PRODUCT =================
def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    reviews = Review.objects.filter(product=product)

    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    if request.method == "POST" and request.user.is_authenticated:

        Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={
                "rating": request.POST.get("rating"),
                "comment": request.POST.get("comment")
            }
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    return render(request, "shop/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "avg_rating": avg_rating
    })


# ================= CART =================
def cart_view(request):

    cart = request.session.get("cart", {})

    items = []

    total = 0

    for pid, qty in cart.items():

        try:
            product = Product.objects.get(id=pid)

        except Product.DoesNotExist:
            continue

        subtotal = product.price * qty

        total += subtotal

        items.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        })

    return render(request, "shop/cart.html", {
        "items": items,
        "total": total
    })


def add_to_cart(request, product_id):

    cart = request.session.get("cart", {})

    cart[str(product_id)] = cart.get(str(product_id), 0) + 1

    request.session["cart"] = cart

    return redirect("cart")


def update_cart(request, product_id, action):

    cart = request.session.get("cart", {})

    pid = str(product_id)

    if pid in cart:

        if action == "increase":
            cart[pid] += 1

        elif action == "decrease":
            cart[pid] -= 1

        if cart[pid] <= 0:
            del cart[pid]

    request.session["cart"] = cart

    return redirect("cart")


def delete_cart(request, product_id):

    cart = request.session.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    request.session["cart"] = cart

    return redirect("cart")


from django.contrib import messages

# ================= CHECKOUT =================
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("home")

    items = []
    total = 0

    for pid, qty in cart.items():

        product = Product.objects.get(id=pid)

        subtotal = product.price * qty

        total += subtotal

        items.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        })

    error = None

    if request.method == "POST":

        customer_name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        # ===== VALIDATE =====

        if not customer_name:
            error = "⚠ Vui lòng nhập tên khách hàng"

        elif not phone:
            error = "⚠ Vui lòng nhập số điện thoại"

        elif not phone.isdigit():
            error = "⚠ Số điện thoại chỉ được nhập số"

        elif len(phone) < 10:
            error = "⚠ Số điện thoại không hợp lệ"

        # ===== NẾU KHÔNG LỖI =====

        if not error:

            order = Order.objects.create(
                customer_name=customer_name,
                phone=phone,
                address=address,
                total_price=total
            )

            for item in items:

                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["product"].price
                )

            # Xóa giỏ hàng
            request.session["cart"] = {}

            return render(request, "shop/order_success.html", {
                "order": order
            })

    return render(request, "shop/checkout.html", {
        "items": items,
        "total": total,
        "error": error
    })


# ================= STAFF LOGIN =================
def staff_login(request):

    if request.method == "POST":

        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user and user.is_staff:

            login(request, user)

            return redirect("staff_dashboard")

        return render(request, "shop/staff_login.html", {
            "error": "Sai tài khoản hoặc không có quyền"
        })

    return render(request, "shop/staff_login.html")


def staff_logout(request):

    logout(request)

    return redirect("staff_login")


# ================= STAFF =================
@login_required
def staff_dashboard(request):

    if not request.user.is_staff:
        return redirect("home")

    orders = Order.objects.all().order_by("-created_at")

    return render(request, "shop/staff_dashboard.html", {
        "orders": orders
    })


@login_required
def create_order(request):

    if not request.user.is_staff:
        return redirect("home")

    products = Product.objects.all()

    if request.method == "POST":

        order = Order.objects.create(user=request.user)

        total = 0

        for product in products:

            qty = request.POST.get(f"qty_{product.id}")

            if qty and int(qty) > 0:

                qty = int(qty)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.price
                )

                total += product.price * qty

        order.total_price = total

        order.save()

        return redirect("staff_dashboard")

    return render(request, "shop/create_order.html", {
        "products": products
    })


@login_required
def approve_order(request, order_id):

    if not request.user.is_staff:
        return redirect("home")

    order = get_object_or_404(Order, id=order_id)

    order.status = "Approved"

    order.save()

    return redirect("staff_dashboard")


@login_required
def reject_order(request, order_id):

    if not request.user.is_staff:
        return redirect("home")

    order = get_object_or_404(Order, id=order_id)

    order.status = "Rejected"

    order.save()

    return redirect("staff_dashboard")


@login_required
def delete_order(request, order_id):

    if not request.user.is_staff:
        return redirect("home")

    get_object_or_404(Order, id=order_id).delete()

    return redirect("staff_dashboard")
