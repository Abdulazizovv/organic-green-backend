#!/usr/bin/env python
import os
import django

# Django sozlamalarini o'rnatamiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Product, ProductCategory
from apps.cart.models import Cart, CartItem
from django.contrib.auth import get_user_model


User = get_user_model()

print("=== Cart Model Test ===")

# Test data yaratamiz
category, _ = ProductCategory.objects.get_or_create(
    name_uz='Test kategoriya',
    defaults={
        'name_ru': 'Test category', 
        'name_en': 'Test category'
    }
)

product, _ = Product.objects.get_or_create(
    name_uz='Test mahsulot',
    defaults={
        'name_ru': 'Test product',
        'name_en': 'Test product',
        'price': 100,
        'stock': 5,  # Faqat 5 ta stock
        'category': category
    }
)

print(f"Product: {product.name_uz}")
print(f"Stock: {product.stock}")

# Cart yaratamiz
cart, _ = Cart.objects.get_or_create(session_key='test-session')
cart.items.all().delete()  # Oldingi itemlarni tozalaymiz

# Cart item yaratamiz
cart_item = CartItem.objects.create(
    cart=cart, 
    product=product, 
    quantity=3
)

print(f"Created cart item: {cart_item.quantity} x {cart_item.product.name_uz}")

# Stock-dan ko'p quantity qo'yishga harakat qilamiz
print("\n=== Testing stock validation ===")
try:
    cart_item.quantity = 10  # Stock (5) dan ko'p
    cart_item.save()
    print("✅ SUCCESS: No ValueError raised from model save")
    print(f"Final quantity: {cart_item.quantity}")
except ValueError as e:
    print(f"❌ ERROR: ValueError still exists: {e}")
except Exception as e:
    print(f"❌ OTHER ERROR: {type(e).__name__}: {e}")

print("\n=== Test completed ===")
