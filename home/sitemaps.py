from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home:home",
            "home:home_page",
            "home:edit_profile",
            "home:reviews",
            "home:logout",
            "home:artists",
            "home:bookings",
        ]

    def location(self, item):
        return reverse(item)
