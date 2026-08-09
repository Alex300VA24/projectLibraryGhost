from django.contrib.auth.models import User
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Identificador')
    display_name = models.CharField(max_length=50, verbose_name='Nombre mostrado')

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.display_name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True, related_name='profiles', verbose_name='Rol')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    colorblind_mode = models.BooleanField(default=False, verbose_name='Modo daltonismo')
    hearing_impaired_mode = models.BooleanField(default=False, verbose_name='Modo discapacidad auditiva')
    must_change_password = models.BooleanField(default=False, verbose_name='Debe cambiar contraseña')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} — {self.role.display_name if self.role else "Sin rol"}'
