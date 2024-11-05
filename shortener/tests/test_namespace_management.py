import pytest
from django.urls import reverse
from shortener.models import Namespace
from django.conf import settings

@pytest.mark.django_db
class TestNamespaceManagement:
    def test_free_user_namespace_creation(self, client, free_user):
        client.force_login(free_user)
        response = client.post(reverse('create_namespace'), {
            'name': 'testspace'
        })
        assert response.status_code == 302
        assert Namespace.objects.filter(name='testspace').exists()

    def test_free_user_short_namespace_restricted(self, client, free_user):
        client.force_login(free_user)
        response = client.post(reverse('create_namespace'), {
            'name': 'ab'  # Too short for free user
        })
        assert response.status_code == 200
        assert "This field can only contain lowercase letters and numbers" in response.content.decode('utf-8')
        assert not Namespace.objects.filter(name='ab').exists()

    def test_paid_user_short_namespace_allowed(self, client, paid_user):
        client.force_login(paid_user)
        response = client.post(reverse('create_namespace'), {
            'name': 'a'
        })
        assert response.status_code == 302
        assert Namespace.objects.filter(name='a').exists()

    def test_namespace_limit_free_user(self, client, free_user):
        client.force_login(free_user)
        # Create namespaces up to the limit
        for i in range(settings.FREE_USER_NAMESPACE_LIMIT):
            Namespace.objects.create(user=free_user, name=f'space{i}')
        
        # Try to create one more
        response = client.post(reverse('create_namespace'), {
            'name': 'onemore'
        })
        assert response.status_code == 200