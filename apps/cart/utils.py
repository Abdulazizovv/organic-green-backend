"""
Cart utilities
Helper functions for cart functionality
"""
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import Cart, CartHistory


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_or_create_cart(request):
    """
    Get or create cart for authenticated user or anonymous session
    
    Returns:
        tuple: (cart, created)
    """
    if request.user.is_authenticated:
        # For authenticated users
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_key': None}
        )
        
        # Merge anonymous cart if exists
        if not created and request.session.session_key:
            try:
                anonymous_cart = Cart.objects.get(
                    session_key=request.session.session_key,
                    user=None
                )
                
                # Merge items from anonymous cart
                for item in anonymous_cart.items.all():
                    cart_item, item_created = cart.items.get_or_create(
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    
                    if not item_created:
                        # Check stock before merging quantities
                        new_quantity = cart_item.quantity + item.quantity
                        if new_quantity <= item.product.stock:
                            cart_item.quantity = new_quantity
                            cart_item.save()
                        else:
                            # If merged quantity exceeds stock, use max available
                            cart_item.quantity = item.product.stock
                            cart_item.save()
                
                # Delete anonymous cart
                anonymous_cart.delete()
                
            except Cart.DoesNotExist:
                pass
        
        return cart, created
    
    else:
        # For anonymous users
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
        
        return cart, created


def log_cart_action(cart, action, product=None, quantity=None, request=None):
    """
    Log cart action for analytics
    
    Args:
        cart: Cart instance
        action: Action type ('add', 'update', 'remove', 'clear', 'checkout')
        product: Product instance (optional)
        quantity: Quantity (optional)
        request: HTTP request (optional)
    """
    try:
        history_data = {
            'cart': cart,
            'action': action,
            'product': product,
            'quantity': quantity
        }
        
        if request:
            history_data.update({
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                'ip_address': get_client_ip(request)
            })
        
        if product:
            # Get current price
            price = product.sale_price if product.sale_price else product.price
            history_data['price'] = price
        
        CartHistory.objects.create(**history_data)
        
    except Exception as e:
        # Log error but don't break the main flow
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error logging cart action: {str(e)}")


def get_cart_summary(cart):
    """
    Get detailed cart summary
    
    Args:
        cart: Cart instance
        
    Returns:
        dict: Cart summary with calculations
    """
    items = cart.items.select_related('product').all()
    
    subtotal = sum(item.product.price * item.quantity for item in items)
    total_discount = sum(
        (item.product.price - item.get_unit_price()) * item.quantity 
        for item in items
    )
    
    return {
        'total_items': cart.total_items,
        'total_price': float(cart.total_price),
        'items_count': cart.items_count,
        'subtotal': float(subtotal),
        'total_discount': float(total_discount),
        'savings': float(total_discount),
        'is_empty': cart.is_empty(),
        'items': [
            {
                'id': str(item.id),
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name_uz,
                    'image': item.product.image.url if item.product.image else None,
                    'slug': item.product.slug
                },
                'quantity': item.quantity,
                'unit_price': float(item.get_unit_price()),
                'original_price': float(item.product.price),
                'total_price': float(item.get_total_price()),
                'is_on_sale': bool(item.product.sale_price),
                'available_stock': item.product.stock,
                'is_available': item.product.stock >= item.quantity
            }
            for item in items
        ]
    }


def transfer_anonymous_cart_to_user(session_key, user):
    """
    Transfer anonymous cart to authenticated user
    
    Args:
        session_key: Session key of anonymous user
        user: User instance
    """
    try:
        anonymous_cart = Cart.objects.get(
            session_key=session_key,
            user=None
        )
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Transfer items
        for item in anonymous_cart.items.all():
            cart_item, item_created = user_cart.items.get_or_create(
                product=item.product,
                defaults={'quantity': item.quantity}
            )
            
            if not item_created:
                cart_item.quantity += item.quantity
                cart_item.save()
        
        # Delete anonymous cart
        anonymous_cart.delete()
        
        return user_cart
        
    except Cart.DoesNotExist:
        # No anonymous cart to transfer
        user_cart, created = Cart.objects.get_or_create(user=user)
        return user_cart


def validate_cart_item_stock(cart_item):
    """
    Validate if cart item quantity is available in stock
    
    Args:
        cart_item: CartItem instance
        
    Returns:
        dict: Validation result
    """
    product = cart_item.product
    
    if not product.is_active:
        return {
            'valid': False,
            'error': 'Mahsulot faol emas',
            'available_stock': 0
        }
    
    if product.stock < cart_item.quantity:
        return {
            'valid': False,
            'error': f'Mahsulot omborda yetarli emas. Mavjud: {product.stock}',
            'available_stock': product.stock
        }
    
    return {
        'valid': True,
        'available_stock': product.stock
    }


def validate_full_cart(cart):
    """
    Validate all items in cart for stock availability
    
    Args:
        cart: Cart instance
        
    Returns:
        dict: Validation result for all items
    """
    validation_results = []
    total_valid = True
    
    for item in cart.items.all():
        result = validate_cart_item_stock(item)
        result['item_id'] = str(item.id)
        result['product_name'] = item.product.name_uz
        result['requested_quantity'] = item.quantity
        
        validation_results.append(result)
        
        if not result['valid']:
            total_valid = False
    
    return {
        'valid': total_valid,
        'items': validation_results,
        'total_items': len(validation_results),
        'valid_items': len([r for r in validation_results if r['valid']]),
        'invalid_items': len([r for r in validation_results if not r['valid']])
    }
