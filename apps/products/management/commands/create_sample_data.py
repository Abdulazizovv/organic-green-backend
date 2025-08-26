"""
Sample data creation script for testing admin interface
"""
from django.core.management.base import BaseCommand
from apps.products.models import ProductCategory, ProductTag, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample product data for testing admin interface'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {
                'name_uz': 'Mevalar',
                'name_ru': 'Фрукты', 
                'name_en': 'Fruits',
                'description_uz': 'Turli xil organik mevalar',
                'description_ru': 'Различные органические фрукты',
                'description_en': 'Various organic fruits'
            },
            {
                'name_uz': 'Sabzavotlar',
                'name_ru': 'Овощи',
                'name_en': 'Vegetables', 
                'description_uz': 'Toza organik sabzavotlar',
                'description_ru': 'Чистые органические овощи',
                'description_en': 'Fresh organic vegetables'
            },
            {
                'name_uz': 'Yong\'oqlar',
                'name_ru': 'Орехи',
                'name_en': 'Nuts',
                'description_uz': 'Tabiiy yong\'oqlar va urug\'lar',
                'description_ru': 'Натуральные орехи и семена',
                'description_en': 'Natural nuts and seeds'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name_uz=cat_data['name_uz'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'✅ Created category: {category.name_uz}')
        
        # Create tags
        tags_data = [
            {'name_uz': 'Organik', 'name_ru': 'Органический', 'name_en': 'Organic'},
            {'name_uz': 'Toza', 'name_ru': 'Свежий', 'name_en': 'Fresh'},
            {'name_uz': 'Mahalliy', 'name_ru': 'Местный', 'name_en': 'Local'},
            {'name_uz': 'Import', 'name_ru': 'Импорт', 'name_en': 'Imported'},
            {'name_uz': 'Premium', 'name_ru': 'Премиум', 'name_en': 'Premium'},
            {'name_uz': 'Eko', 'name_ru': 'Эко', 'name_en': 'Eco'},
        ]
        
        tags = []
        for tag_data in tags_data:
            tag, created = ProductTag.objects.get_or_create(
                name_uz=tag_data['name_uz'],
                defaults=tag_data
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'🏷️  Created tag: {tag.name_uz}')
        
        # Create products
        products_data = [
            {
                'name_uz': 'Organik olma',
                'name_ru': 'Органическое яблоко',
                'name_en': 'Organic apple',
                'description_uz': 'Toza organik qizil olma, pestisidsiz',
                'description_ru': 'Чистое органическое красное яблоко, без пестицидов',
                'description_en': 'Pure organic red apple, pesticide-free',
                'price': Decimal('12.50'),
                'sale_price': Decimal('10.00'),
                'stock': 150,
                'category': categories[0],  # Fruits
                'is_featured': True,
                'tags': [tags[0], tags[1], tags[2]]  # Organic, Fresh, Local
            },
            {
                'name_uz': 'Toza sabzi',
                'name_ru': 'Свежая морковь',
                'name_en': 'Fresh carrot',
                'description_uz': 'Mahalliy toza sabzi, vitaminlarga boy',
                'description_ru': 'Местная свежая морковь, богатая витаминами',
                'description_en': 'Local fresh carrot, rich in vitamins',
                'price': Decimal('8.00'),
                'stock': 200,
                'category': categories[1],  # Vegetables
                'tags': [tags[1], tags[2]]  # Fresh, Local
            },
            {
                'name_uz': 'Premium yong\'oq',
                'name_ru': 'Премиум грецкий орех',
                'name_en': 'Premium walnut',
                'description_uz': 'Yuqori sifatli import yong\'oq',
                'description_ru': 'Высококачественный импортный грецкий орех',
                'description_en': 'High quality imported walnut',
                'price': Decimal('45.00'),
                'sale_price': Decimal('40.00'),
                'stock': 50,
                'category': categories[2],  # Nuts
                'is_featured': True,
                'tags': [tags[3], tags[4]]  # Imported, Premium
            },
            {
                'name_uz': 'Organik pomidor',
                'name_ru': 'Органический помидор',
                'name_en': 'Organic tomato',
                'description_uz': 'Eko toza pomidor, tabiiy o\'stirilgan',
                'description_ru': 'Эко чистый помидор, выращенный естественным путем',
                'description_en': 'Eco clean tomato, naturally grown',
                'price': Decimal('15.00'),
                'stock': 5,  # Low stock for testing
                'category': categories[1],  # Vegetables
                'tags': [tags[0], tags[5]]  # Organic, Eco
            },
            {
                'name_uz': 'Quruq anjir',
                'name_ru': 'Сушеный инжир',
                'name_en': 'Dried fig',
                'description_uz': 'Tabiiy quritilgan shirinlik',
                'description_ru': 'Натурально высушенный инжир',
                'description_en': 'Naturally dried fig',
                'price': Decimal('25.00'),
                'stock': 0,  # Out of stock for testing
                'category': categories[0],  # Fruits
                'is_active': False,  # Inactive for testing
                'tags': [tags[0], tags[4]]  # Organic, Premium
            }
        ]
        
        products = []
        for prod_data in products_data:
            tags_to_add = prod_data.pop('tags', [])
            product, created = Product.objects.get_or_create(
                name_uz=prod_data['name_uz'],
                defaults=prod_data
            )
            if created:
                product.tags.set(tags_to_add)
                products.append(product)
                self.stdout.write(f'📦 Created product: {product.name_uz}')
        
        # Add suggested products relationships
        if len(products) >= 3:
            products[0].suggested_products.add(products[1], products[2])
            products[1].suggested_products.add(products[0])
            self.stdout.write('🔗 Added suggested products relationships')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created sample data:\n'
                f'   📁 {len(categories)} categories\n'
                f'   🏷️  {len(tags)} tags\n'
                f'   📦 {len(products)} products\n\n'
                f'Admin panel: http://localhost:8001/admin/\n'
                f'Username: admin\n'
                f'Password: admin123'
            )
        )
