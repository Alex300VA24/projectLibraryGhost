from django.db import migrations, models
import django.db.models.deletion


ROLES = {
    'admin': 'Administrador',
    'employee': 'Empleado',
    'client': 'Cliente',
}


def populate_roles(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    for name, display_name in ROLES.items():
        Role.objects.create(name=name, display_name=display_name)


def migrate_role_data(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    Role = apps.get_model('accounts', 'Role')
    role_map = {
        'admin': 'admin',
        'administrador': 'admin',
        'employee': 'employee',
        'empleado': 'employee',
        'client': 'client',
        'cliente': 'client',
    }
    for profile in UserProfile.objects.all():
        old_role = profile.role or 'client'
        target = role_map.get(old_role, 'client')
        profile.role_new = Role.objects.get(name=target)
        profile.save(update_fields=['role_new'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='Identificador')),
                ('display_name', models.CharField(max_length=50, verbose_name='Nombre mostrado')),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(populate_roles),
        migrations.AddField(
            model_name='userprofile',
            name='role_new',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profiles', to='accounts.role', verbose_name='Rol'),
        ),
        migrations.RunPython(migrate_role_data),
        migrations.RemoveField(
            model_name='userprofile',
            name='role',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='role_new',
            new_name='role',
        ),
    ]
