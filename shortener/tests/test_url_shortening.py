import pytest
from django.urls import reverse
from shortener.models import ShortenedURL
from django.conf import settings

@pytest.mark.django_db
class TestURLShortening:
    def test_shorten_url_free_user(self, client, free_user, free_user_namespace):
        client.force_login(free_user)
        response = client.post(reverse('shorten_url', kwargs={'namespace_id': free_user_namespace.id}), {
            'original_url': 'https://www.example.com',
            'keyword': 'test'
        })
        assert response.status_code == 302, f"Expected status code 302 but got {response.status_code}. Response content: {response.content}"
        assert ShortenedURL.objects.filter(shortened_path='test').exists()

    def test_url_limit_free_user(self, client, free_user, free_user_namespace):
        client.force_login(free_user)
        # Create URLs up to the limit
        for i in range(settings.FREE_USER_URL_LIMIT):
            ShortenedURL.objects.create(
                namespace=free_user_namespace,
                original_url='https://www.example.com',
                shortened_path=f'test{i}'
            )
        
        # Try to create one more
        response = client.post(reverse('shorten_url', kwargs={'namespace_id': free_user_namespace.id}), {
            'original_url': 'https://www.example.com',
            'shortened_path': 'onemore'
        })
        assert response.status_code == 200
        assert "You have reached maximum URLs limit of" in response.content.decode('utf-8')
       

    def test_url_redirection(self, client, shortened_url):
        response = client.get(reverse('redirect_shortened_url', kwargs={
            'namespace_name': shortened_url.namespace.name,
            'shortened_path': shortened_url.shortened_path
        }))
        assert response.status_code == 302
        assert response.url == shortened_url.original_url 