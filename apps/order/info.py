"""
Order API Information
Get order API information and documentation
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def order_info(request):
    """
    Get order API information
    """
    return Response({
        'title': 'Buyurtma API',
        'description': 'Buyurtmalar boshqaruvi uchun API',
        'endpoints': {
            'list_orders': '/api/orders/ (GET)',
            'order_detail': '/api/orders/{id}/ (GET)',
            'create_order': '/api/orders/create_order/ (POST)',
            'cancel_order': '/api/orders/{id}/cancel/ (POST)',
            'order_stats': '/api/orders/stats/ (GET)',
        },
        'features': [
            'Authenticated va anonymous users uchun',
            'Cart dan avtomatik order yaratish',
            'Stock nazorati',
            'Order bekor qilish',
            'Batafsil order tarixi',
            'Paginatsiya qo\'llab-quvvatlash'
        ],
        'payment_methods': [
            'cod - Naqd / Kuryerga',
            'click - Click',
            'payme - Payme', 
            'card - Bank karta',
            'none - To\'lovsiz'
        ],
        'order_statuses': [
            'pending - Kutilmoqda',
            'paid - To\'langan',
            'processing - Qayta ishlanmoqda',
            'shipped - Jo\'natildi',
            'delivered - Yetkazildi',
            'canceled - Bekor qilindi'
        ]
    })
