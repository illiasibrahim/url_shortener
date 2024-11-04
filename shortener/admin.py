from django.contrib import admin

from shortener.models import Namespace, ShortenedURL

admin.site.register(Namespace)
admin.site.register(ShortenedURL)
