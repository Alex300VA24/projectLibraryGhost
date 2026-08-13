from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.orders.models import Order, OrderHistory, OrderItem, OrderStatus
from apps.products.models import Category, Product
from .models import Expense


User = get_user_model()


class DashboardStatsApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dashboard_test', password='secret')
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        today = timezone.localtime(timezone.now()).date()
        now = timezone.localtime(timezone.now())

        Order.objects.create(user=self.user, status=OrderStatus.COMPLETED, total='100.00', updated_at=now, created_at=now)
        Expense.objects.create(concept='Gasto hoy', type='Variable', amount='20.00', date=today, created_by=self.user)
        Expense.objects.create(concept='Gasto semana', type='Fijo', amount='30.00', date=today - timedelta(days=1), created_by=self.user)
        Expense.objects.create(concept='Gasto mes', type='Operativo', amount='40.00', date=today - timedelta(days=15), created_by=self.user)

    def test_dashboard_stats_returns_period_metrics(self):
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/api/stats/')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertAlmostEqual(data['ventasHoy'], 100.0)
        self.assertAlmostEqual(data['gastosHoy'], 20.0)
        self.assertAlmostEqual(data['gananciaHoy'], 80.0)
        self.assertAlmostEqual(data['gastosSemana'], 50.0)
        self.assertAlmostEqual(data['gananciaSemana'], 50.0)
        self.assertAlmostEqual(data['gastosMes'], 50.0)
        self.assertAlmostEqual(data['gananciaMes'], -50.0)


class DashboardSaleCancellationApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sale_test', password='secret')
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        category = Category.objects.create(name='Libros')
        self.product = Product.objects.create(
            category=category,
            name='Libro de prueba',
            price='25.00',
            stock=7,
        )
        self.order = Order.objects.create(
            user=self.user,
            created_by=self.user,
            status=OrderStatus.COMPLETED,
            payment_method='cash',
            total='50.00',
            is_paid=True,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            quantity=2,
            price='25.00',
        )
        self.client.force_login(self.user)

    def test_cancel_sale_persists_status_and_restores_stock_once(self):
        url = f'/dashboard/api/ventas/{self.order.id}/cancelar/'
        response = self.client.post(
            url,
            data='{"justificacion":"Error de registro"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.CANCELLED)
        self.assertEqual(self.product.stock, 9)
        self.assertTrue(
            OrderHistory.objects.filter(
                order=self.order,
                to_status=OrderStatus.CANCELLED,
            ).exists()
        )

        second_response = self.client.post(url, data='{}', content_type='application/json')
        self.assertEqual(second_response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)
