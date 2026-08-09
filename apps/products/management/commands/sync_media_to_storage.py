from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        'Sube los archivos de MEDIA_ROOT al storage activo (por ejemplo '
        'Supabase Storage en producción), conservando las rutas relativas '
        'para que coincidan con las que ya guarda la base de datos.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Re-subir los archivos aunque ya existan en el storage.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Solo mostrar qué se subiría, sin subir nada.',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']

        if not settings.MEDIA_ROOT.exists():
            self.stderr.write(
                f'No existe MEDIA_ROOT: {settings.MEDIA_ROOT}'
            )
            return

        if isinstance(default_storage, FileSystemStorage) and not force:
            self.stderr.write(
                self.style.WARNING(
                    'El storage activo es el filesystem local. '
                    'Ejecuta este comando con USE_SUPABASE_STORAGE=True '
                    'para subir a Supabase (o usa --force).'
                )
            )

        files = [p for p in settings.MEDIA_ROOT.rglob('*') if p.is_file()]
        if not files:
            self.stdout.write('No hay archivos en MEDIA_ROOT.')
            return

        uploaded = skipped = failed = 0
        for path in files:
            name = path.relative_to(settings.MEDIA_ROOT).as_posix()
            if not force and default_storage.exists(name):
                skipped += 1
                self.stdout.write(f'Ya existe: {name}')
                continue
            if dry_run:
                self.stdout.write(f'Se subiría: {name}')
                uploaded += 1
                continue
            try:
                with path.open('rb') as fh:
                    default_storage.save(name, File(fh))
                uploaded += 1
                self.stdout.write(self.style.SUCCESS(f'Subido: {name}'))
            except Exception as exc:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f'Error en {name}: {exc}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Listo: {uploaded} subidos, {skipped} ya existían, '
                f'{failed} con error.'
            )
        )
