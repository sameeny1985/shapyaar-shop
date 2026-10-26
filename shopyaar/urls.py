from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from store.sitemaps import ProductSitemap, StaticSitemap


def google_verification(request):
    content = "google-site-verification: googleff764f24dc120cc.html"
    return HttpResponse(content, content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("googleff764f24dc120cc.html", google_verification),
    path("", include("store.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "products": ProductSitemap,
                "static": StaticSitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

# Security: temporary make-admin / fix-empty-usernames endpoints removed

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
