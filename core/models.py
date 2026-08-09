from django.db import models
from django.conf import settings
from library_ghostitzer.storage_backends import get_documents_storage


class Expense(models.Model):
    TYPE_CHOICES = [
        ('Fijo', 'Fijo'),
        ('Variable', 'Variable'),
        ('Operativo', 'Operativo'),
        ('Mantenimiento', 'Mantenimiento'),
    ]

    concept = models.CharField(max_length=200, verbose_name='Concepto')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    date = models.DateField(verbose_name='Fecha')
    description = models.TextField(blank=True, verbose_name='Descripción')
    comprobante = models.FileField(
        upload_to='comprobantes/',
        storage=get_documents_storage,
        blank=True, null=True,
        verbose_name='Comprobante',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.concept} - S/ {self.amount}'
