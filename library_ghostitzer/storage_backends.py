"""
Custom storage backends for Supabase S3-compatible storage.
- ProductsStorage  → bucket 'productos'   (imágenes de productos y categorías) — público
- DocumentsStorage → bucket 'documentos'  (comprobantes de gastos) — privado, signed URLs
"""
import os
from storages.backends.s3 import S3Storage

# Tiempo de validez de las signed URLs para comprobantes (en segundos)
SIGNED_URL_EXPIRY = int(os.getenv('COMPROBANTE_SIGNED_URL_EXPIRY', 300))  # 5 minutos


def _common_options():
    return {
        'access_key': os.getenv('SUPABASE_S3_ACCESS_KEY_ID', ''),
        'secret_key': os.getenv('SUPABASE_S3_SECRET_ACCESS_KEY', ''),
        'endpoint_url': os.getenv('SUPABASE_S3_ENDPOINT_URL', ''),
        'region_name': os.getenv('SUPABASE_S3_REGION_NAME', 'us-east-1'),
        'file_overwrite': False,
        'client_config_kwargs': {
            'request_checksum_calculation': 'when_required',
        },
    }


class ProductsStorage(S3Storage):
    """Bucket público — imágenes de productos y categorías."""
    def __init__(self, **kwargs):
        options = _common_options()
        options.update({
            'bucket_name': os.getenv('SUPABASE_STORAGE_BUCKET_PRODUCTOS', 'productos'),
            'default_acl': 'public-read',
            'querystring_auth': False,
        })
        options.update(kwargs)
        super().__init__(**options)


class DocumentsStorage(S3Storage):
    """
    Bucket privado — comprobantes de gastos.
    querystring_auth=True activa las signed URLs automáticamente al llamar .url()
    """
    def __init__(self, **kwargs):
        options = _common_options()
        options.update({
            'bucket_name': os.getenv('SUPABASE_STORAGE_BUCKET_DOCUMENTOS', 'documentos'),
            'default_acl': 'private',
            'querystring_auth': True,
            'signature_version': 's3v4',
            'expiration': SIGNED_URL_EXPIRY,
        })
        options.update(kwargs)
        super().__init__(**options)


def get_signed_url(field_file) -> str | None:
    """
    Genera una signed URL temporal para un FileField que usa DocumentsStorage.
    Devuelve None si el campo está vacío.
    Uso: get_signed_url(gasto.comprobante)
    """
    if not field_file:
        return None
    storage = field_file.storage
    return storage.url(field_file.name)
