from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import ProductCategory, Product, ProductImage
from decimal import Decimal
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test data for products, categories, and users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new test data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            ProductCategory.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        self.stdout.write('Creating test data...')
        
        # Create test users
        self.create_test_users()
        
        # Create categories
        categories = self.create_categories()
        
        # Create products
        self.create_products(categories)
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))

    def create_test_users(self):
        """Create test users"""
        self.stdout.write('Creating test users...')
        
        # Regular user
        user1, created = User.objects.get_or_create(
            username='testuser1',
            defaults={
                'email': 'test1@example.com',
                'first_name': 'Anvar',
                'last_name': 'Karimov',
                'phone': '+998901234567',
                'is_verified': True
            }
        )
        if created:
            user1.set_password('testpass123')
            user1.save()
            self.stdout.write(f'Created user: {user1.username}')

        # Another user
        user2, created = User.objects.get_or_create(
            username='testuser2',
            defaults={
                'email': 'test2@example.com',
                'first_name': 'Malika',
                'last_name': 'Nazarova',
                'phone': '+998907654321',
                'is_verified': False
            }
        )
        if created:
            user2.set_password('testpass123')
            user2.save()
            self.stdout.write(f'Created user: {user2.username}')

    def create_categories(self):
        """Create product categories"""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            {
                'name_uz': 'Mevalar',
                'name_ru': 'Фрукты',
                'name_en': 'Fruits',
                'description_uz': 'Yangi va mazali mevalar',
                'description_ru': 'Свежие и вкусные фрукты',
                'description_en': 'Fresh and delicious fruits',
            },
            {
                'name_uz': 'Sabzavotlar',
                'name_ru': 'Овощи',
                'name_en': 'Vegetables',
                'description_uz': 'Organik sabzavotlar',
                'description_ru': 'Органические овощи',
                'description_en': 'Organic vegetables',
            },
            {
                'name_uz': 'Yashilliklar',
                'name_ru': 'Зелень',
                'name_en': 'Greens',
                'description_uz': 'Yangi yashilliklar va dorivor o\'tlar',
                'description_ru': 'Свежая зелень и травы',
                'description_en': 'Fresh greens and herbs',
            },
            {
                'name_uz': 'Yong\'oqlar',
                'name_ru': 'Орехи',
                'name_en': 'Nuts',
                'description_uz': 'Quruq mevalar va yong\'oqlar',
                'description_ru': 'Сухофрукты и орехи',
                'description_en': 'Dried fruits and nuts',
            }
        ]

        categories = {}
        for i, cat_data in enumerate(categories_data):
            category, created = ProductCategory.objects.get_or_create(
                name_uz=cat_data['name_uz'],
                defaults=cat_data
            )
            # Use the English name as key for easier reference
            categories[cat_data['name_en'].lower()] = category
            if created:
                self.stdout.write(f'Created category: {category.name_uz}')

        return categories

    def create_products(self, categories):
        """Create test products"""
        self.stdout.write('Creating products...')
        
        products_data = [
            # Fruits
            {
                'name_uz': 'Olma',
                'name_ru': 'Яблоко',
                'name_en': 'Apple',
                'description_uz': 'Yangi va shirin olma',
                'description_ru': 'Свежие и сладкие яблоки',
                'description_en': 'Fresh and sweet apples',
                'category': 'fruits',
                'price': Decimal('15000'),
                'sale_price': Decimal('12000'),
                'stock': 100,
            },
            {
                'name_uz': 'Banan',
                'name_ru': 'Банан',
                'name_en': 'Banana',
                'description_uz': 'Tropik banan',
                'description_ru': 'Тропические бананы',
                'description_en': 'Tropical bananas',
                'category': 'fruits',
                'price': Decimal('18000'),
                'stock': 80,
            },
            {
                'name_uz': 'Apelsin',
                'name_ru': 'Апельсин',
                'name_en': 'Orange',
                'description_uz': 'C vitamini bilan boy apelsin',
                'description_ru': 'Апельсины богатые витамином C',
                'description_en': 'Oranges rich in vitamin C',
                'category': 'fruits',
                'price': Decimal('20000'),
                'sale_price': Decimal('17000'),
                'stock': 60,
            },
            
            # Vegetables
            {
                'name_uz': 'Kartoshka',
                'name_ru': 'Картофель',
                'name_en': 'Potato',
                'description_uz': 'Yangi kartoshka',
                'description_ru': 'Свежий картофель',
                'description_en': 'Fresh potatoes',
                'category': 'vegetables',
                'price': Decimal('8000'),
                'stock': 200,
            },
            {
                'name_uz': 'Sabzi',
                'name_ru': 'Морковь',
                'name_en': 'Carrot',
                'description_uz': 'Shirin sabzi',
                'description_ru': 'Сладкая морковь',
                'description_en': 'Sweet carrots',
                'category': 'vegetables',
                'price': Decimal('10000'),
                'sale_price': Decimal('8500'),
                'stock': 150,
            },
            {
                'name_uz': 'Pomidor',
                'name_ru': 'Помидор',
                'name_en': 'Tomato',
                'description_uz': 'Qizil pomidor',
                'description_ru': 'Красные помидоры',
                'description_en': 'Red tomatoes',
                'category': 'vegetables',
                'price': Decimal('12000'),
                'stock': 120,
            },
            
            # Greens
            {
                'name_uz': 'Jambil',
                'name_ru': 'Укроп',
                'name_en': 'Dill',
                'description_uz': 'Yangi jambil',
                'description_ru': 'Свежий укроп',
                'description_en': 'Fresh dill',
                'category': 'greens',
                'price': Decimal('5000'),
                'stock': 50,
            },
            {
                'name_uz': 'Kashnich',
                'name_ru': 'Кориандр',
                'name_en': 'Cilantro',
                'description_uz': 'Xushbo\'y kashnich',
                'description_ru': 'Ароматный кориандр',
                'description_en': 'Aromatic cilantro',
                'category': 'greens',
                'price': Decimal('4000'),
                'sale_price': Decimal('3500'),
                'stock': 40,
            },
            
            # Nuts
            {
                'name_uz': 'Yong\'oq',
                'name_ru': 'Грецкий орех',
                'name_en': 'Walnut',
                'description_uz': 'Mazali yong\'oq',
                'description_ru': 'Вкусные грецкие орехи',
                'description_en': 'Delicious walnuts',
                'category': 'nuts',
                'price': Decimal('45000'),
                'sale_price': Decimal('40000'),
                'stock': 30,
            },
            {
                'name_uz': 'Bodom',
                'name_ru': 'Миндаль',
                'name_en': 'Almond',
                'description_uz': 'Shirinlaw bodom',
                'description_ru': 'Сладкий миндаль',
                'description_en': 'Sweet almonds',
                'category': 'nuts',
                'price': Decimal('55000'),
                'stock': 25,
            }
        ]

        for product_data in products_data:
            category_name = product_data.pop('category')
            category = categories[category_name]
            
            product, created = Product.objects.get_or_create(
                name_uz=product_data['name_uz'],
                category=category,
                defaults={
                    **product_data,
                    'slug': product_data['name_en'].lower().replace(' ', '-'),
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name_uz}')

        self.stdout.write(self.style.SUCCESS(f'Created {len(products_data)} products'))
