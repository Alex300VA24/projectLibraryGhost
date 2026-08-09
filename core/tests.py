from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.orders.models import Order, OrderStatus
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
