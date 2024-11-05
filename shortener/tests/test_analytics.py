import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestAnalytics:
    def test_url_analytics_tracking(self, client, shortened_url):
        # Make multiple requests to the shortened URL
        for _ in range(3):
            client.get(reverse('redirect_shortened_url', kwargs={
                'namespace_name': shortened_url.namespace.name,
                'shortened_path': shortened_url.shortened_path
            }))
        
        shortened_url.refresh_from_db()
        assert shortened_url.access_count == 3
        assert shortened_url.access_logs.count() == 3

    def test_analytics_view_access(self, client, shortened_url):
        client.force_login(shortened_url.namespace.user)
        response = client.get(reverse('url_analytics', kwargs={
            'namespace_id': shortened_url.namespace.id,
            'url_id': shortened_url.id
        }))
        assert response.status_code == 200