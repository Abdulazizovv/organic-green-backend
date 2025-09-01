# Cart API Documentation

Savat (Shopping Cart) API - foydalanuvchilar uchun xarid savati boshqaruvi.

## Asosiy imkoniyatlar

- ✅ Tizimga kirgan va kirimagan foydalanuvchilar uchun savat
- ✅ Mahsulotlarni savatga qo'shish/o'chirish
- ✅ Miqdorni yangilash
- ✅ Avtomatik narx hisoblash (chegirmalar bilan)
- ✅ Stok nazorati
- ✅ Savat tarixi
- ✅ Session-based anonymous carts
- ✅ Authenticated user cart persistence

## API Endpointlari

### 1. Joriy savatni olish
**GET** `/api/cart/current/`

```json
{
    "id": "uuid",
    "owner": {
        "type": "registered", // yoki "anonymous"
        "username": "foydalanuvchi_nomi",
        "email": "email@example.com"
    },
    "items": [
        {
            "id": "uuid",
            "product": {
                "id": "uuid",
                "name_uz": "Mahsulot nomi",
                "price": 10000.00,
                "sale_price": 8000.00,
                "current_price": 8000.00,
                "is_on_sale": true,
                "stock": 100,
                "image_url": "http://example.com/image.jpg"
            },
            "quantity": 2,
            "unit_price": 8000.00,
            "total_price": 16000.00,
            "is_available": true,
            "max_quantity": 100,
            "added_at": "2025-08-26T12:00:00Z"
        }
    ],
    "total_items": 2,
    "total_price": 16000.00,
    "items_count": 1,
    "is_empty": false,
    "created_at": "2025-08-26T12:00:00Z",
    "updated_at": "2025-08-26T12:05:00Z"
}
```

### 2. Savatga mahsulot qo'shish
**POST** `/api/cart/add_item/`

```json
{
    "product_id": "uuid",
    "quantity": 2
}
```

**Javob:**
```json
{
    "message": "Mahsulot savatga qo'shildi",
    "item": {
        "id": "uuid",
        "product": { /* product details */ },
        "quantity": 2,
        "unit_price": 8000.00,
        "total_price": 16000.00
    },
    "cart_summary": {
        "total_items": 2,
        "total_price": 16000.00,
        "items_count": 1
    }
}
```

### 3. Mahsulot miqdorini yangilash
**PATCH** `/api/cart/update_item/`

```json
{
    "item_id": "uuid",
    "quantity": 5
}
```

### 4. Mahsulotni savatdan o'chirish
**DELETE** `/api/cart/remove_item/?item_id=uuid`

### 5. Savatni tozalash
**DELETE** `/api/cart/clear/`

### 6. Savat xulosasi
**GET** `/api/cart/summary/`

```json
{
    "total_items": 3,
    "total_price": 23000.00,
    "items_count": 2,
    "is_empty": false,
    "subtotal": 25000.00,
    "total_discount": 2000.00,
    "items_summary": [
        {
            "product_name": "Mahsulot 1",
            "quantity": 2,
            "unit_price": 8000.00,
            "total_price": 16000.00,
            "is_on_sale": true
        },
        {
            "product_name": "Mahsulot 2",
            "quantity": 1,
            "unit_price": 7000.00,
            "total_price": 7000.00,
            "is_on_sale": false
        }
    ]
}
```

### 7. Savat tarixi
**GET** `/api/cart/history/`

```json
{
    "history": [
        {
            "id": "uuid",
            "action": "add",
            "action_display": "Qo'shildi",
            "product": "uuid",
            "product_name": "Mahsulot nomi",
            "quantity": 2,
            "price": 8000.00,
            "formatted_price": 8000.00,
            "timestamp": "2025-08-26T12:00:00Z"
        }
    ],
    "count": 10
}
```

## Xususiyatlar

### Anonymous vs Authenticated Users

#### Anonymous foydalanuvchilar:
- Session key asosida savat yaratiladi
- Browser session davomida saqlanadi
- Session tugagach yo'qoladi

#### Authenticated foydalanuvchilar:
- User ID asosida savat yaratiladi
- Doimiy saqlanadi
- Anonymous savat bilan birlashtirish

### Stok nazorati

Har qanday amal bajarilishidan oldin mahsulot stoki tekshiriladi:

```json
// Agar stok yetarli bo'lmasa
{
    "error": "Mahsulot omborda yetarli emas. Mavjud: 5"
}
```

### Avtomatik narx hisoblash

- Agar `sale_price` mavjud bo'lsa, u ishlatiladi
- Aks holda `price` ishlatiladi
- Chegirmalar avtomatik hisoblanadi

### Session Management

Anonymous foydalanuvchilar uchun Django session framework ishlatiladi:

```python
# views.py da
if not request.session.session_key:
    request.session.create()
```

## Frontend bilan ishlash

### React/JavaScript misoli

```javascript
// Cart service
class CartService {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
    }
    
    async getCurrentCart() {
        const response = await fetch(`${this.baseURL}/cart/current/`);
        return response.json();
    }
    
    async addItem(productId, quantity = 1) {
        const response = await fetch(`${this.baseURL}/cart/add_item/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getToken()}`
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });
        return response.json();
    }
    
    async updateItem(itemId, quantity) {
        const response = await fetch(`${this.baseURL}/cart/update_item/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getToken()}`
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: quantity
            })
        });
        return response.json();
    }
    
    async removeItem(itemId) {
        const response = await fetch(
            `${this.baseURL}/cart/remove_item/?item_id=${itemId}`,
            {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            }
        );
        return response.json();
    }
    
    async clearCart() {
        const response = await fetch(`${this.baseURL}/cart/clear/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`
            }
        });
        return response.json();
    }
    
    getToken() {
        return localStorage.getItem('access_token');
    }
}

// React hook misoli
import { useState, useEffect } from 'react';

export const useCart = () => {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const cartService = new CartService();
    
    useEffect(() => {
        loadCart();
    }, []);
    
    const loadCart = async () => {
        try {
            setLoading(true);
            const cartData = await cartService.getCurrentCart();
            setCart(cartData);
        } catch (error) {
            console.error('Cart loading error:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const addToCart = async (productId, quantity = 1) => {
        try {
            const result = await cartService.addItem(productId, quantity);
            await loadCart(); // Reload cart
            return result;
        } catch (error) {
            console.error('Add to cart error:', error);
            throw error;
        }
    };
    
    const updateCartItem = async (itemId, quantity) => {
        try {
            const result = await cartService.updateItem(itemId, quantity);
            await loadCart(); // Reload cart
            return result;
        } catch (error) {
            console.error('Update cart error:', error);
            throw error;
        }
    };
    
    const removeFromCart = async (itemId) => {
        try {
            const result = await cartService.removeItem(itemId);
            await loadCart(); // Reload cart
            return result;
        } catch (error) {
            console.error('Remove from cart error:', error);
            throw error;
        }
    };
    
    const clearCart = async () => {
        try {
            const result = await cartService.clearCart();
            await loadCart(); // Reload cart
            return result;
        } catch (error) {
            console.error('Clear cart error:', error);
            throw error;
        }
    };
    
    return {
        cart,
        loading,
        addToCart,
        updateCartItem,
        removeFromCart,
        clearCart,
        reloadCart: loadCart
    };
};
```

## Testlar

Testlarni ishga tushirish:

```bash
python manage.py test apps.cart.test_cart --settings=core.test_settings -v 2
```

## Security

- CSRF protection
- Input validation
- SQL injection protection
- XSS protection
- Rate limiting

## Performance

- Database query optimization
- Proper indexing
- Caching (Redis)
- Pagination for history

## Error Handling

API barcha xatolarni standard formatda qaytaradi:

```json
{
    "error": "Xato tavsifi",
    "details": {
        "field": ["Maydon xatosi"]
    }
}
```

## Monitoring

Cart API quyidagi actionlarni log qiladi:
- `add` - Mahsulot qo'shildi
- `update` - Miqdor yangilandi  
- `remove` - Mahsulot o'chirildi
- `clear` - Savat tozalandi
- `checkout` - Xarid qilindi
