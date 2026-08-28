```python
"""
Custom Cloudinary Storage for Shopyaar

این Storage برای ذخیره تصاویر محصولات، دسته‌بندی‌ها
و گالری محصولات در Cloudinary استفاده می‌شود.

ویژگی‌ها:
- حفظ پسوند اصلی فایل
- تشخیص فرمت واقعی تصویر
- پشتیبانی از JPG / JPEG / PNG / WEBP / GIF / BMP / TIFF
- جلوگیری از تداخل نام فایل‌ها
- استفاده از نام فایل اصلی
- ذخیره مستقیم در Cloudinary
"""

import os
import uuid
import mimetypes

from django.core.files.storage import Storage
from django.core.files.base import ContentFile

import cloudinary
import cloudinary.uploader
import cloudinary.api


class OriginalExtensionCloudinaryStorage(Storage):
    """
    Custom Cloudinary Storage

    این Storage فایل را دریافت کرده و با پسوند اصلی
    آن در Cloudinary ذخیره می‌کند.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self, *args, **kwargs):

        super().__init__()

        self.cloud_name = os.environ.get(
            'CLOUDINARY_CLOUD_NAME',
            ''
        )

        self.api_key = os.environ.get(
            'CLOUDINARY_API_KEY',
            ''
        )

        self.api_secret = os.environ.get(
            'CLOUDINARY_API_SECRET',
            ''
        )

        # تنظیم Cloudinary
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )

    # ========================================================
    # SAVE
    # ========================================================

    def _save(self, name, content):
        """
        ذخیره فایل در Cloudinary

        name:
            نام اصلی فایل

        content:
            فایل آپلود شده
        """

        # ----------------------------------------------------
        # گرفتن نام فایل
        # ----------------------------------------------------

        original_name = os.path.basename(name)

        # ----------------------------------------------------
        # گرفتن extension
        # ----------------------------------------------------

        extension = os.path.splitext(
            original_name
        )[1].lower()

        # ----------------------------------------------------
        # اگر extension وجود نداشت
        # ----------------------------------------------------

        if not extension:

            extension = self._detect_extension(
                content
            )

        # ----------------------------------------------------
        # حذف نقطه از ابتدای extension
        # ----------------------------------------------------

        extension_without_dot = extension.lstrip(
            '.'
        )

        # ----------------------------------------------------
        # فرمت‌های مجاز
        # ----------------------------------------------------

        allowed_formats = {

            'jpg',
            'jpeg',
            'png',
            'webp',
            'gif',
            'bmp',
            'tif',
            'tiff',

        }

        # ----------------------------------------------------
        # اگر فرمت ناشناخته بود
        # ----------------------------------------------------

        if extension_without_dot not in allowed_formats:

            detected_extension = self._detect_extension(
                content
            )

            if detected_extension:

                extension = detected_extension

                extension_without_dot = (
                    extension.lstrip('.')
                )

        # ----------------------------------------------------
        # نام بدون extension
        # ----------------------------------------------------

        base_name = os.path.splitext(
            original_name
        )[0]

        # ----------------------------------------------------
        # پاک کردن path احتمالی
        # ----------------------------------------------------

        base_name = os.path.basename(
            base_name
        )

        # ----------------------------------------------------
        # اگر نام خالی بود
        # ----------------------------------------------------

        if not base_name:

            base_name = 'image'

        # ----------------------------------------------------
        # ساخت شناسه یکتا
        # ----------------------------------------------------

        unique_id = uuid.uuid4().hex[:12]

        public_id = (
            f"{base_name}_{unique_id}"
        )

        # ----------------------------------------------------
        # حفظ موقعیت فعلی فایل
        # ----------------------------------------------------

        try:

            content.seek(0)

        except Exception:

            pass

        # ----------------------------------------------------
        # مشخص کردن Resource Type
        # ----------------------------------------------------

        resource_type = 'image'

        # ----------------------------------------------------
        # مشخص کردن format
        # ----------------------------------------------------

        upload_options = {

            'resource_type': resource_type,

            'public_id': public_id,

            'use_filename': False,

            'unique_filename': False,

            'overwrite': False,

            'secure': True,

        }

        # ----------------------------------------------------
        # فقط اگر extension معتبر داریم
        # ----------------------------------------------------

        if extension_without_dot in allowed_formats:

            upload_options['format'] = (
                extension_without_dot
            )

        # ----------------------------------------------------
        # تعیین folder
        # ----------------------------------------------------

        folder = self._get_folder(
            name
        )

        if folder:

            upload_options['folder'] = folder

        # ----------------------------------------------------
        # Upload to Cloudinary
        # ----------------------------------------------------

        result = cloudinary.uploader.upload(
            content,
            **upload_options
        )

        # ----------------------------------------------------
        # دریافت public_id
        # ----------------------------------------------------

        returned_public_id = result.get(
            'public_id'
        )

        returned_format = result.get(
            'format'
        )

        returned_resource_type = result.get(
            'resource_type',
            'image'
        )

        # ----------------------------------------------------
        # اگر Cloudinary فرمت برگرداند
        # از همان استفاده می‌کنیم
        # ----------------------------------------------------

        if returned_format:

            final_extension = (
                '.' + returned_format.lower()
            )

        elif extension:

            final_extension = extension

        else:

            final_extension = ''

        # ----------------------------------------------------
        # نامی که Django در Database ذخیره می‌کند
        # ----------------------------------------------------

        if returned_public_id:

            django_name = (
                returned_public_id
                + final_extension
            )

        else:

            django_name = (
                public_id
                + final_extension
            )

        # ----------------------------------------------------
        # normalize path
        # ----------------------------------------------------

        django_name = django_name.replace(
            '\\',
            '/'
        )

        return django_name

    # ========================================================
    # DETECT EXTENSION
    # ========================================================

    def _detect_extension(self, content):
        """
        تشخیص پسوند واقعی فایل.

        ابتدا MIME type را بررسی می‌کند.
        در صورت امکان header فایل را نیز بررسی می‌کند.
        """

        try:

            content.seek(0)

        except Exception:

            pass

        # ----------------------------------------------------
        # خواندن چند بایت اول فایل
        # ----------------------------------------------------

        try:

            header = content.read(32)

        except Exception:

            header = b''

        finally:

            try:

                content.seek(0)

            except Exception:

                pass

        # ----------------------------------------------------
        # JPEG
        # ----------------------------------------------------

        if header.startswith(
            b'\xff\xd8\xff'
        ):

            return '.jpg'

        # ----------------------------------------------------
        # PNG
        # ----------------------------------------------------

        if header.startswith(
            b'\x89PNG\r\n\x1a\n'
        ):

            return '.png'

        # ----------------------------------------------------
        # GIF
        # ----------------------------------------------------

        if (
            header.startswith(b'GIF87a')
            or
            header.startswith(b'GIF89a')
        ):

            return '.gif'

        # ----------------------------------------------------
        # WEBP
        # ----------------------------------------------------

        if (
            len(header) >= 12
            and
            header[0:4] == b'RIFF'
            and
            header[8:12] == b'WEBP'
        ):

            return '.webp'

        # ----------------------------------------------------
        # BMP
        # ----------------------------------------------------

        if header.startswith(
            b'BM'
        ):

            return '.bmp'

        # ----------------------------------------------------
        # TIFF
        # ----------------------------------------------------

        if (
            header.startswith(b'II*\x00')
            or
            header.startswith(b'MM\x00*')
        ):

            return '.tiff'

        # ----------------------------------------------------
        # MIME type
        # ----------------------------------------------------

        mime_type = None

        try:

            if hasattr(content, 'content_type'):

                mime_type = content.content_type

        except Exception:

            mime_type = None

        # ----------------------------------------------------
        # MIME -> Extension
        # ----------------------------------------------------

        mime_extensions = {

            'image/jpeg': '.jpg',

            'image/jpg': '.jpg',

            'image/png': '.png',

            'image/webp': '.webp',

            'image/gif': '.gif',

            'image/bmp': '.bmp',

            'image/tiff': '.tiff',

        }

        if mime_type in mime_extensions:

            return mime_extensions[
                mime_type
            ]

        # ----------------------------------------------------
        # Unknown
        # ----------------------------------------------------

        return ''

    # ========================================================
    # GET FOLDER
    # ========================================================

    def _get_folder(self, name):
        """
        تعیین folder در Cloudinary براساس مسیر فایل.

        products/
            -> shopyaar/products

        products/gallery/
            -> shopyaar/products/gallery

        categories/
            -> shopyaar/categories
        """

        normalized_name = name.replace(
            '\\',
            '/'
        )

        normalized_name = normalized_name.strip(
            '/'
        )

        directory = os.path.dirname(
            normalized_name
        )

        if not directory:

            return 'shopyaar'

        directory = directory.strip(
            '/'
        )

        return (
            'shopyaar/'
            + directory
        )

    # ========================================================
    # URL
    # ========================================================

    def url(self, name):
        """
        ساخت URL مستقیم Cloudinary
        """

        if not name:

            return ''

        normalized_name = name.replace(
            '\\',
            '/'
        )

        # ----------------------------------------------------
        # جدا کردن extension
        # ----------------------------------------------------

        public_id_with_extension = (
            normalized_name
        )

        # ----------------------------------------------------
        # Cloudinary public_id
        # ----------------------------------------------------

        public_id = public_id_with_extension

        extension = ''

        known_extensions = [

            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
            '.gif',
            '.bmp',
            '.tif',
            '.tiff',

        ]

        lower_name = public_id.lower()

        for ext in known_extensions:

            if lower_name.endswith(ext):

                extension = ext

                public_id = public_id[
                    :-len(ext)
                ]

                break

        # ----------------------------------------------------
        # ساخت URL
        # ----------------------------------------------------

        try:

            return cloudinary.CloudinaryImage(
                public_id
            ).build_url(
                secure=True,
                resource_type='image',
                format=(
                    extension.lstrip('.')
                    if extension
                    else None
                )
            )

        except Exception:

            return ''


    # ========================================================
    # EXISTS
    # ========================================================

    def exists(self, name):
        """
        بررسی وجود فایل در Cloudinary
        """

        if not name:

            return False

        normalized_name = name.replace(
            '\\',
            '/'
        )

        public_id = normalized_name

        known_extensions = [

            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
            '.gif',
            '.bmp',
            '.tif',
            '.tiff',

        ]

        lower_name = public_id.lower()

        for ext in known_extensions:

            if lower_name.endswith(ext):

                public_id = public_id[
                    :-len(ext)
                ]

                break

        try:

            cloudinary.api.resource(
                public_id,
                resource_type='image'
            )

            return True

        except Exception:

            return False

    # ========================================================
    # DELETE
    # ========================================================

    def delete(self, name):
        """
        حذف تصویر از Cloudinary
        """

        if not name:

            return

        normalized_name = name.replace(
            '\\',
            '/'
        )

        public_id = normalized_name

        known_extensions = [

            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
            '.gif',
            '.bmp',
            '.tif',
            '.tiff',

        ]

        lower_name = public_id.lower()

        for ext in known_extensions:

            if lower_name.endswith(ext):

                public_id = public_id[
                    :-len(ext)
                ]

                break

        try:

            cloudinary.uploader.destroy(
                public_id,
                resource_type='image'
            )

        except Exception:

            pass

    # ========================================================
    # OPEN
    # ========================================================

    def _open(self, name, mode='rb'):
        """
        باز کردن فایل از Cloudinary
        """

        from django.core.files.base import ContentFile
        import requests

        url = self.url(name)

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        return ContentFile(
            response.content,
            name=os.path.basename(name)
        )

    # ========================================================
    # SIZE
    # ========================================================

    def size(self, name):
        """
        دریافت حجم فایل
        """

        import requests

        url = self.url(name)

        response = requests.head(
            url,
            timeout=30
        )

        response.raise_for_status()

        content_length = response.headers.get(
            'Content-Length'
        )

        if content_length:

            return int(content_length)

        return 0

    # ========================================================
    # ACCESSIBILITY
    # ========================================================

    def get_accessed_time(self, name):

        raise NotImplementedError(
            'Cloudinary does not provide accessed time.'
        )

    def get_created_time(self, name):

        raise NotImplementedError(
            'Cloudinary does not provide created time.'
        )

    def get_modified_time(self, name):

        raise NotImplementedError(
            'Cloudinary does not provide modified time.'
        )
```
