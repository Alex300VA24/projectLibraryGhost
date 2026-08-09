from django.core.management.base import BaseCommand
from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Carga 5 productos de ejemplo con códigos de barras para probar la API de escáner'

    def handle(self, *args, **options):
        categoria, _ = Category.objects.get_or_create(
            name='Bebidas',
            defaults={'description': 'Bebidas y gaseosas'}
        )
        categoria2, _ = Category.objects.get_or_create(
            name='Abarrotes',
            defaults={'description': 'Productos de abarrotes'}
        )

        productos = [
            {
                'codigo': '7501234567890',
                'name': 'Coca Cola 600ml',
                'price': 18.50,
                'stock': 42,
                'description': 'Bebida gaseosa',
                'category': categoria,
            },
            {
                'codigo': '7750123456789',
                'name': 'Inca Kola 500ml',
                'price': 16.00,
                'stock': 35,
                'description': 'Bebida gaseosa amarilla',
                'category': categoria,
            },
            {
                'codigo': '7801234567890',
                'name': 'Arroz Costeño 1kg',
                'price': 4.50,
                'stock': 100,
                'description': 'Arroz extra superior',
                'category': categoria2,
            },
            {
                'codigo': '7901234567890',
                'name': 'Aceite Primor 1L',
                'price': 12.90,
                'stock': 60,
                'description': 'Aceite vegetal',
                'category': categoria2,
            },
            {
                'codigo': '7012345678905',
                'name': 'Fideos Don Vittorio 500g',
                'price': 3.20,
                'stock': 80,
                'description': 'Fideos tallarín',
                'category': categoria2,
            },
        ]

        creados = 0
        for data in productos:
            _, created = Product.objects.get_or_create(
                codigo=data['codigo'],
                defaults=data,
            )
            if created:
                creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Productos de ejemplo cargados: {creados} creados, '
            f'{len(productos) - creados} ya existían.'
        ))
