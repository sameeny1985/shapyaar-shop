from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from pathlib import Path

# اگر اپ account داری و make_admin می‌خواهی، این خط را نگه دار:
try:
    from account.views import make_admin
except ImportError:
    try:
        from accounts.views import make_admin
    except ImportError:
        make_admin = None


def google_verification(request):
    file_path = Path(settings.BASE_DIR) / 'googleff764f24dc120cc.html'
    if file_path.exists():
        return HttpResponse(
            file_path.read_text(encoding='utf-8'),
            content_type='text/html'
        )
    return HttpResponse('Verification file not found', status=404)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('googleff764f24dc120cc.html', google_verification),
    path('', include('store.urls')),
]

if make_admin is not None:
    urlpatterns.insert(2, path('make-admin-now/', make_admin, name='make_admin'))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
