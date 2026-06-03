"""
URL configuration for ras project.
"""

import sys

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve
from django.views.generic import TemplateView

from home.sitemaps import StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
}


urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("emp/", include("employee.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("wallet/", include("wallet.urls")),
    path("", include("home.urls")),
)

handler404 = "home.views.custom_404"

if settings.DEBUG or "runserver" in sys.argv:
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$",
            serve,
            {"document_root": settings.STATICFILES_DIRS[0]},
        ),
    ]
    if getattr(settings, "MEDIA_URL", None) and getattr(settings, "MEDIA_ROOT", None):
        urlpatterns += [
            re_path(
                r"^media/(?P<path>.*)$",
                serve,
                {"document_root": settings.MEDIA_ROOT},
            ),
        ]
