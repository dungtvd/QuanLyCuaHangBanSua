from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    Product,
    Order,
    OrderItem,
    Banner,
    Review
)


# ================= CATEGORY =================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'image_preview'
    )

    search_fields = (
        'name',
    )

    def image_preview(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" width="50"/>',
                obj.image.url
            )

        return "No Image"

    image_preview.short_description = "Ảnh"


# ================= PRODUCT =================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'stock',
        'stock_status',
        'image_preview'
    )

    list_filter = (
        'category',
    )

    search_fields = (
        'name',
    )

    list_editable = (
        'price',
        'stock'
    )

    def stock_status(self, obj):

        if obj.stock == 0:
            return "❌ Hết hàng"

        if obj.stock < 10:
            return "⚠️ Sắp hết"

        return "✔ Còn hàng"

    stock_status.short_description = "Trạng thái"

    def image_preview(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" width="50"/>',
                obj.image.url
            )

        return "No Image"

    image_preview.short_description = "Ảnh"


# ================= BANNER =================
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'title',
        'image_preview',
        'active'
    )

    def image_preview(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" width="100"/>',
                obj.image.url
            )

        return "No Image"

    image_preview.short_description = "Ảnh"


# ================= REVIEW =================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'product',
        'rating',
        'created_at'
    )

    search_fields = (
        'product__name',
        'user__username'
    )

    list_filter = (
        'rating',
    )


# ================= ORDER ITEM INLINE =================
class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0


# ================= ORDER =================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'phone',
        'total_price',
        'status',
        'created_at',
        'item_count'
    )

    list_filter = (
        'status',
        'created_at'
    )

    search_fields = (
        'customer_name',
        'phone'
    )

    inlines = [
        OrderItemInline
    ]

    actions = [
        'mark_approved',
        'mark_rejected'
    ]

    def item_count(self, obj):

        return obj.items.count()

    item_count.short_description = "Số SP"

    def mark_approved(self, request, queryset):

        queryset.update(status='Approved')

    mark_approved.short_description = "✔ Duyệt đơn"

    def mark_rejected(self, request, queryset):

        queryset.update(status='Rejected')

    mark_rejected.short_description = "❌ Hủy đơn"


# ================= ORDER ITEM =================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'product',
        'quantity',
        'price'
    )

    search_fields = (
        'product__name',
    )