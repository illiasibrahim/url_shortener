# url_tracking_middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import ShortenedURL, URLAccessLog
from django.db.models import Count
from django.utils import timezone


class URLTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Split the path to get namespace and shortened_path (e.g., /namespace/shortened_path/)
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 2:
            namespace = path_parts[0]
            shortened_path = path_parts[1]

            try:
                # Get the ShortenedURL object based on the namespace and shortened_path
                shortened_url = ShortenedURL.objects.get(
                    namespace__name=namespace,
                    shortened_path=shortened_path
                )

                # Increment access count
                shortened_url.access_count += 1
                shortened_url.save(update_fields=['access_count'])

                # Log access details
                ip_address = request.META.get('REMOTE_ADDR')
                is_unique = not shortened_url.access_logs.filter(
                    ip_address=ip_address).exists()

                # Create a new URLAccessLog entry
                URLAccessLog.objects.create(
                    url=shortened_url,
                    ip_address=ip_address,
                    is_unique=is_unique
                )

                # Update unique visitor count if this is a unique visit
                if is_unique:
                    shortened_url.unique_visitors += 1
                    shortened_url.save(update_fields=['unique_visitors'])

                # Store the shortened_url in request for use in process_response
                request.shortened_url = shortened_url

            except ShortenedURL.DoesNotExist:
                pass  # Let the view handle non-existent URLs

    def process_response(self, request, response):
        # Check if we processed a shortened URL and it responded successfully
        if hasattr(request, 'shortened_url') and response.status_code == 302:
            shortened_url = request.shortened_url

            # Increment success count
            shortened_url.success_count += 1
            shortened_url.save(update_fields=['success_count'])

        return response
