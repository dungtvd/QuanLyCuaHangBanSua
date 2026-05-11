from django.contrib import admin
from django.urls import path
from shop import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ===== ADMIN =====
    path('admin/', admin.site.urls),

    # ===== HOME =====
    path('', views.home, name="home"),

    # ===== PRODUCT =====
    path('product/<int:product_id>/', views.product_detail, name="product_detail"),

    # ===== CART =====
    path('cart/', views.cart_view, name="cart"),
    path('add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart, name="update_cart"),
    path('cart/delete/<int:product_id>/', views.delete_cart, name="delete_cart"),

    # ===== CHECKOUT =====
    path('checkout/', views.checkout, name="checkout"),

    # ===== STAFF =====
    path('staff/login/', views.staff_login, name="staff_login"),
    path('staff/logout/', views.staff_logout, name="staff_logout"),

    # DASHBOARD
    path('staff/', views.staff_dashboard, name="staff_dashboard"),

    # ORDER MANAGEMENT
    path('staff/create/', views.create_order, name="create_order"),
    path('staff/approve/<int:order_id>/', views.approve_order, name="approve_order"),
    path('staff/reject/<int:order_id>/', views.reject_order, name="reject_order"),
    path('staff/delete/<int:order_id>/', views.delete_order, name="delete_order"),
]

# ===== MEDIA =====
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)