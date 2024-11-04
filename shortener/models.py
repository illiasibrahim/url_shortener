# shortener/models.py
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.db import models


class Namespace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class ShortenedURL(models.Model):
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE)
    original_url = models.URLField()
    shortened_path = models.CharField(max_length=256)
    access_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.namespace}/{self.shortened_path}"

    def get_shortened_url(self, request):
        return f"{request.scheme}://{request.get_host()}/{self.namespace}/{self.shortened_path}"


class URLAccessLog(models.Model):
    url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name="access_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_unique = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Get location data using GeoIP
        geo = GeoIP2()
        if self.ip_address:
            try:
                location = geo.city(self.ip_address)
                self.country = location.get('country_name')
                self.region = location.get('region')
                self.city = location.get('city')
            except Exception:
                pass
        super().save(*args, **kwargs)
