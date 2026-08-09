import os

from storages.backends.s3 import S3Storage


# Tiempo de validez de las signed URLs para comprobantes
SIGNED_URL_EXPIRY = int(
    os.getenv("COMPROBANTE_SIGNED_URL_EXPIRY", "300")
)


def _common_options():
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


class ProductsStorage(S3Storage):
    """Bucket público para imágenes de productos y categorías."""

    def __init__(self, **kwargs):
        options = _common_options()

        options.update({
            "bucket_name": os.getenv(
                "SUPABASE_STORAGE_BUCKET_PRODUCTOS",
                "productos"
            ),
            "querystring_auth": False,
        })

        options.update(kwargs)

        super().__init__(**options)


class DocumentsStorage(S3Storage):
    """
    Bucket privado para comprobantes.

    querystring_auth=True genera URLs firmadas
    cuando se utiliza .url().
    """

    def __init__(self, **kwargs):
        options = _common_options()

        options.update({
            "bucket_name": os.getenv(
                "SUPABASE_STORAGE_BUCKET_DOCUMENTOS",
                "documentos"
            ),
            "querystring_auth": True,
            "signature_version": "s3v4",
            "querystring_expire": SIGNED_URL_EXPIRY,
        })

        options.update(kwargs)

        super().__init__(**options)


def get_signed_url(field_file) -> str | None:
    """
    Genera una signed URL temporal para un FileField.
    """

    if not field_file:
        return None

    return field_file.storage.url(field_file.name)


def get_products_storage():
    """Storage para imágenes de productos y categorías."""

    from django.conf import settings

    if getattr(settings, "USE_SUPABASE_STORAGE", False):
        return ProductsStorage()

    from django.core.files.storage import FileSystemStorage

    return FileSystemStorage()


def get_documents_storage():
    """Storage para documentos y comprobantes."""

    from django.conf import settings

    if getattr(settings, "USE_SUPABASE_STORAGE", False):
        return DocumentsStorage()

    from django.core.files.storage import FileSystemStorage

    return FileSystemStorage()