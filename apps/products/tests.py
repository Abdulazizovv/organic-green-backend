from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from .models import Product, ProductCategory, ProductTag


class ProductCategoryModelTest(TestCase):
    """ProductCategory modeli uchun testlar"""
    
    def setUp(self):
        """Har bir test uchun tayyorgarlik"""
        self.category_data = {
            'name_uz': 'Mevalar',
            'name_ru': 'Фрукты',
            'name_en': 'Fruits',
            'description_uz': 'Yangi mevalar',
            'description_ru': 'Свежие фрукты',
            'description_en': 'Fresh fruits'
        }
    
    def test_create_category(self):
        """Kategoriya yaratish testi"""
        category = ProductCategory.objects.create(**self.category_data)
        
        self.assertEqual(category.name_uz, 'Mevalar')
        self.assertEqual(category.name_ru, 'Фрукты')
        self.assertEqual(category.name_en, 'Fruits')
        self.assertEqual(str(category), 'Mevalar')
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_category_string_representation(self):
        """Kategoriya string ko'rinishi testi"""
        category = ProductCategory.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Mevalar')
    
    def test_category_without_description(self):
        """Tavsifisiz kategoriya testi"""
        category_data = {
            'name_uz': 'Sabzavotlar',
            'name_ru': 'Овощи',
            'name_en': 'Vegetables'
        }
        category = ProductCategory.objects.create(**category_data)
        
        self.assertIsNone(category.description_uz)
        self.assertIsNone(category.description_ru)
        self.assertIsNone(category.description_en)


class ProductTagModelTest(TestCase):
    """ProductTag modeli uchun testlar"""
    
    def setUp(self):
        """Har bir test uchun tayyorgarlik"""
        self.tag_data = {
            'name_uz': 'Organik',
            'name_ru': 'Органический',
            'name_en': 'Organic'
        }
    
    def test_create_tag(self):
        """Tag yaratish testi"""
        tag = ProductTag.objects.create(**self.tag_data)
        
        self.assertEqual(tag.name_uz, 'Organik')
        self.assertEqual(tag.name_ru, 'Органический')
        self.assertEqual(tag.name_en, 'Organic')
        self.assertEqual(str(tag), 'Organik')
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)
    
    def test_tag_string_representation(self):
        """Tag string ko'rinishi testi"""
        tag = ProductTag.objects.create(**self.tag_data)
        self.assertEqual(str(tag), 'Organik')


class ProductModelTest(TestCase):
    """Product modeli uchun testlar"""
    
    def setUp(self):
        """Har bir test uchun tayyorgarlik"""
        # Kategoriya yaratish
        self.category = ProductCategory.objects.create(
            name_uz='Mevalar',
            name_ru='Фрукты',
            name_en='Fruits'
        )
        
        # Tag yaratish
        self.tag1 = ProductTag.objects.create(
            name_uz='Organik',
            name_ru='Органический',
            name_en='Organic'
        )
        
        self.tag2 = ProductTag.objects.create(
            name_uz='Yangi',
            name_ru='Свежий',
            name_en='Fresh'
        )
        
        # Mahsulot ma'lumotlari
        self.product_data = {
            'name_uz': 'Olma',
            'name_ru': 'Яблоко',
            'name_en': 'Apple',
            'description_uz': 'Mazali qizil olma',
            'description_ru': 'Вкусное красное яблоко',
            'description_en': 'Delicious red apple',
            'price': Decimal('15000.00'),
            'stock': 100,
            'category': self.category,
            'is_active': True,
            'is_featured': False
        }
    
    def test_create_product(self):
        """Mahsulot yaratish testi"""
        product = Product.objects.create(**self.product_data)
        
        self.assertEqual(product.name_uz, 'Olma')
        self.assertEqual(product.name_ru, 'Яблоко')
        self.assertEqual(product.name_en, 'Apple')
        self.assertEqual(product.price, Decimal('15000.00'))
        self.assertEqual(product.stock, 100)
        self.assertEqual(product.category, self.category)
        self.assertTrue(product.is_active)
        self.assertFalse(product.is_featured)
        self.assertEqual(str(product), 'Olma')
    
    def test_product_with_sale_price(self):
        """Chegirma narxi bilan mahsulot testi"""
        self.product_data['sale_price'] = Decimal('12000.00')
        product = Product.objects.create(**self.product_data)
        
        self.assertEqual(product.sale_price, Decimal('12000.00'))
        self.assertLess(product.sale_price, product.price)
    
    def test_product_with_tags(self):
        """Taglar bilan mahsulot testi"""
        product = Product.objects.create(**self.product_data)
        product.tags.add(self.tag1, self.tag2)
        
        self.assertEqual(product.tags.count(), 2)
        self.assertIn(self.tag1, product.tags.all())
        self.assertIn(self.tag2, product.tags.all())
    
    def test_product_category_relationship(self):
        """Mahsulot-kategoriya bog'lanish testi"""
        product = Product.objects.create(**self.product_data)
        
        # Kategoriya orqali mahsulotni olish
        category_products = self.category.products.all()
        self.assertIn(product, category_products)
        
        # Mahsulot kategoriyasini tekshirish
        self.assertEqual(product.category, self.category)
    
    def test_suggested_products(self):
        """Tavsiya qilingan mahsulotlar testi"""
        # Ikkinchi mahsulot yaratish
        product1 = Product.objects.create(**self.product_data)
        
        product2_data = self.product_data.copy()
        product2_data['name_uz'] = 'Nok'
        product2_data['name_ru'] = 'Груша'
        product2_data['name_en'] = 'Pear'
        product2 = Product.objects.create(**product2_data)
        
        # Tavsiya qilish
        product1.suggested_products.add(product2)
        
        self.assertIn(product2, product1.suggested_products.all())
        self.assertIn(product1, product2.suggested_for.all())
    
    def test_product_string_representation(self):
        """Mahsulot string ko'rinishi testi"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(str(product), 'Olma')
    
    def test_product_default_values(self):
        """Mahsulot standart qiymatlar testi"""
        minimal_data = {
            'name_uz': 'Test mahsulot',
            'name_ru': 'Тестовый продукт',
            'name_en': 'Test product',
            'price': Decimal('10000.00'),
            'category': self.category
        }
        product = Product.objects.create(**minimal_data)
        
        self.assertEqual(product.stock, 0)  # default value
        self.assertTrue(product.is_active)  # default value
        self.assertFalse(product.is_featured)  # default value
        self.assertIsNone(product.sale_price)
    
    def test_product_timestamps(self):
        """Mahsulot vaqt belgilari testi"""
        product = Product.objects.create(**self.product_data)
        
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
        
        # created_at va updated_at dastlab bir xil bo'lishi kerak
        self.assertEqual(product.created_at, product.updated_at)
    
    def test_product_without_optional_fields(self):
        """Ixtiyoriy maydonlarsiz mahsulot testi"""
        minimal_data = {
            'name_uz': 'Minimal mahsulot',
            'name_ru': 'Минимальный продукт',
            'name_en': 'Minimal product',
            'price': Decimal('5000.00'),
            'category': self.category
        }
        product = Product.objects.create(**minimal_data)
        
        self.assertIsNone(product.description_uz)
        self.assertIsNone(product.description_ru)
        self.assertIsNone(product.description_en)
        self.assertIsNone(product.sale_price)
        self.assertEqual(product.tags.count(), 0)
