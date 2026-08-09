"""
Custom storage backends for Supabase S3-compatible storage.

- ProductsStorage  -> bucket 'productos'
  Imágenes de productos y categorías.
  Bucket público.

- DocumentsStorage -> bucket 'documentos'
  Comprobantes de gastos.
  Bucket privado con signed URLs.
"""

import os

from storages.backends.s3 import S3Storage


# ============================================================
# CONFIGURACIÓN
# ============================================================

SIGNED_URL_EXPIRY = int(
    os.getenv(
        "COMPROBANTE_SIGNED_URL_EXPIRY",
        "300"
    )
)


def _common_options():
    """
    Configuración común para Supabase Storage mediante S3.
    """

    return {
        "access_key": os.getenv(
            "SUPABASE_S3_ACCESS_KEY_ID",
            ""
        ),

        "secret_key": os.getenv(
            "SUPABASE_S3_SECRET_ACCESS_KEY",
            ""
        ),

        "endpoint_url": os.getenv(
            "SUPABASE_S3_ENDPOINT_URL",
            ""
        ),

        "region_name": os.getenv(
            "SUPABASE_S3_REGION_NAME",
            "us-east-1"
        ),

        "file_overwrite": False,
    }


# ============================================================
# PRODUCTOS
# ============================================================

class ProductsStorage(S3Storage):
    """
    Storage para imágenes públicas.

    Bucket:
        productos

    Las imágenes se suben mediante S3,
    pero sus URLs se sirven mediante
    el endpoint público de Supabase.
    """

    def __init__(self, **kwargs):

        options = _common_options()

        options.update({
            "bucket_name": os.getenv(
                "SUPABASE_STORAGE_BUCKET_PRODUCTOS",
                "productos"
            ),

            # No generar signed URLs para productos
            "querystring_auth": False,
        })

        options.update(kwargs)

        super().__init__(**options)

    def url(
        self,
        name,
        parameters=None,
        expire=None,
        http_method=None
    ):
        """
        Devuelve la URL pública de Supabase Storage.

        Ejemplo:

        https://xxxxx.supabase.co/storage/v1/object/public/
        productos/products/imagen.jpg
        """

        project_url = os.getenv(
            "SUPABASE_URL",
            ""
        ).rstrip("/")

        bucket = os.getenv(
            "SUPABASE_STORAGE_BUCKET_PRODUCTOS",
            "productos"
        )

        return (
            f"{project_url}/storage/v1/object/public/"
            f"{bucket}/{name}"
        )


# ============================================================
# DOCUMENTOS
# ============================================================

class DocumentsStorage(S3Storage):
    """
    Storage para documentos privados.

    Bucket:
        documentos

    Los archivos son privados y .url() genera
    una signed URL temporal.
    """

    def __init__(self, **kwargs):

        options = _common_options()

        options.update({
            "bucket_name": os.getenv(
                "SUPABASE_STORAGE_BUCKET_DOCUMENTOS",
                "documentos"
            ),

            # Activar signed URLs
            "querystring_auth": True,

            # Supabase S3 utiliza S3 Signature V4
            "signature_version": "s3v4",

            # Tiempo de validez de la URL
            "querystring_expire": SIGNED_URL_EXPIRY,
        })

        options.update(kwargs)

        super().__init__(**options)


# ============================================================
# SIGNED URL
# ============================================================

def get_signed_url(field_file):
    """
    Genera una signed URL temporal para un FileField
    que utiliza DocumentsStorage.

    Ejemplo:

        url = get_signed_url(gasto.comprobante)
    """

    if not field_file:
        return None

    if not field_file.name:
        return None

    storage = field_file.storage

    return storage.url(field_file.name)


# ============================================================
# STORAGE DE PRODUCTOS
# ============================================================

def get_products_storage():
    """
    Devuelve el storage para imágenes de productos
    y categorías.

    Si USE_SUPABASE_STORAGE=False,
    utiliza almacenamiento local.
    """

    from django.conf import settings

    if getattr(
        settings,
        "USE_SUPABASE_STORAGE",
        False
    ):
        return ProductsStorage()

    from django.core.files.storage import FileSystemStorage

    return FileSystemStorage()


# ============================================================
# STORAGE DE DOCUMENTOS
# ============================================================

def get_documents_storage():
    """
    Devuelve el storage para documentos y comprobantes.

    Si USE_SUPABASE_STORAGE=False,
    utiliza almacenamiento local.
    """

    from django.conf import settings

    if getattr(
        settings,
        "USE_SUPABASE_STORAGE",
        False
    ):
        return DocumentsStorage()

    from django.core.files.storage import FileSystemStorage

    return FileSystemStorage()