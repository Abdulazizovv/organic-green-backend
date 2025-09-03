from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.order.models import Order, OrderItem
from apps.products.models import Product
from decimal import Decimal
import random
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample orders for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of orders to create (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get users and products
        users = list(User.objects.filter(is_superuser=False))
        products = list(Product.objects.filter(is_active=True))
        
        if not users:
            self.stdout.write(self.style.ERROR('No regular users found. Please create test users first.'))
            return
            
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please create test products first.'))
            return

        self.stdout.write(f'Creating {count} sample orders...')
        
        statuses = ['pending', 'paid', 'processing', 'shipped', 'delivered']
        payment_methods = ['cod', 'click', 'payme', 'card']
        
        for i in range(count):
            # Random user or None for anonymous orders
            user = random.choice(users) if random.choice([True, False]) else None
            session_key = f'test_session_{i}' if not user else None
            
            # Random status and payment method
            status = random.choice(statuses)
            payment_method = random.choice(payment_methods)
            
            # Create order
            order = Order.objects.create(
                user=user,
                session_key=session_key,
                status=status,
                payment_method=payment_method,
                full_name=f'Test Customer {i+1}' if not user else f'{user.first_name} {user.last_name}',
                contact_phone=f'+99890123456{i%10}',
                delivery_address=f'Test Address {i+1}, Tashkent',
                notes=f'Test order #{i+1}' if random.choice([True, False]) else '',
            )
            
            # Add 1-5 random products to order
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            total_amount = Decimal('0')
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.sale_price if product.sale_price else product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name_uz,
                    quantity=quantity,
                    unit_price=unit_price,
                    is_sale_price=bool(product.sale_price),
                )
                
                total_amount += unit_price * quantity
            
            # Update order totals
            order.subtotal = total_amount
            order.total_amount = total_amount
            order.save()
            
            user_info = f'User: {user.username}' if user else f'Anonymous (session: {session_key})'
            self.stdout.write(f'Created order {order.order_number} - {user_info} - {status} - {total_amount} UZS')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} sample orders!'))
