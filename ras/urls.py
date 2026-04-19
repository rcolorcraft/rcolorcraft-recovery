"""
URL configuration for ras project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse
from home import sitemaps
from home.sitemaps import StaticViewSitemap
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static


sitemaps = {
    "static": StaticViewSitemap,
    # You can add more sitemaps here if needed
}

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    # path("set_language/", set_language, name="set_language"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("home.urls")),
]
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    # ✅ employee FIRST (IMPORTANT)
    path("emp/", include("employee.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("wallet/", include("wallet.urls")),
    # ✅ home LAST
    path("", include("home.urls")),
)
# STATIC add करो outside i18n
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
