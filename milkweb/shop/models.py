from django.db import models
from django.contrib.auth.models import User


# ================= CATEGORY =================
class Category(models.Model):

    name = models.CharField(max_length=255)

    image = models.ImageField(
        upload_to='category/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# ================= PRODUCT =================
class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    stock = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ================= BANNER =================
class Banner(models.Model):

    title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    image = models.ImageField(upload_to='banners/')

    active = models.BooleanField(default=True)

    def __str__(self):

        if self.title:
            return self.title

        return "Banner"


# ================= ORDER =================
class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Đang chờ'),
        ('Approved', 'Hoàn thành'),
        ('Rejected', 'Đã hủy'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    customer_name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField(blank=True)

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def update_total(self):

        total = sum(
            item.price * item.quantity
            for item in self.items.all()
        )

        self.total_price = total

        self.save()

    def __str__(self):

        if self.customer_name:
            return f"Order #{self.id} - {self.customer_name}"

        if self.user:
            return f"Order #{self.id} - {self.user.username}"

        return f"Order #{self.id}"


# ================= ORDER ITEM =================
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    def save(self, *args, **kwargs):

        if not self.pk:

            if self.product.stock < self.quantity:
                raise ValueError("Không đủ hàng trong kho")

            self.product.stock -= self.quantity
            self.product.save()

        super().save(*args, **kwargs)

        self.order.update_total()

    def delete(self, *args, **kwargs):

        self.product.stock += self.quantity
        self.product.save()

        super().delete(*args, **kwargs)

        self.order.update_total()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ================= REVIEW =================
class Review(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(default=5)

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"