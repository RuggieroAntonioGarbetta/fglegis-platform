from django.contrib.sitemaps import Sitemap
from .models import PraticaImmobiliare

class PraticaSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PraticaImmobiliare.objects.all()

    def lastmod(self, obj):
        return obj.data_creazione
