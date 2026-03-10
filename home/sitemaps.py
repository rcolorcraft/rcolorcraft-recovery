from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "homehome_page",
            "edit_profile",
            "reviews",
            "logout",
            "artists",
            "bookings",
        ]

    def location(self, item):
        return reverse(item)
