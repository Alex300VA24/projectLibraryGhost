import getpass
import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Role


class Command(BaseCommand):
    help = (
        "Crea un superusuario con nombre, apellido, email, teléfono, "
        "contraseña y rol admin."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', default=None, help='Nombre de usuario.',
        )
        parser.add_argument(
            '--email', default=None, help='Correo electrónico.',
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_true',
            help='No prompts for input.',
        )

    def get_input_data(self, prompt, is_password=False):
        if is_password:
            return getpass.getpass(prompt)
        return input(prompt).strip()

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        noinput = options.get('noinput', False)

        if noinput:
            if not username or not email:
                raise CommandError(
                    "Con --noinput necesitas --username y --email."
                )
            first_name = ''
            last_name = ''
            phone = ''
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
            self.stdout.write(
                self.style.WARNING(
                    f"Contraseña generada: {password}"
                )
            )
        else:
            while not username:
                username = self.get_input_data("Nombre de usuario: ")

            while not email:
                email = self.get_input_data("Correo electrónico: ")

            first_name = self.get_input_data("Nombres: ")
            last_name = self.get_input_data("Apellidos: ")
            phone = self.get_input_data("Teléfono: ")

            while True:
                password = self.get_input_data("Contraseña: ", is_password=True)
                password2 = self.get_input_data(
                    "Confirmar contraseña: ", is_password=True
                )
                if password != password2:
                    self.stderr.write("Las contraseñas no coinciden.\n")
                    continue
                try:
                    validate_password(password)
                except Exception as e:
                    self.stderr.write("\n".join(e.messages) + "\n")
                    continue
                break

        user = self.UserModel(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        profile = user.profile
        profile.role = Role.objects.get(name='admin')
        profile.phone = phone
        profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario '{username}' creado exitosamente."
            )
        )
