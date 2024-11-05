import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from shortener.models import Namespace, ShortenedURL
from accounts.models import UserProfile
from faker import Faker

faker = Faker()

@pytest.fixture
def free_user(db):
    user = User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password='testpass123'
    )
    return user


@pytest.fixture
def paid_user(db):
    user = User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password='testpass123'
    )

    UserProfile.objects.create(
        user=user,
    )

    UserProfile.objects.create(
        user=user,
        subscription_plan=UserProfile.PAID,
        expires_on=timezone.now() + timezone.timedelta(days=30)
    )
    
    return user


@pytest.fixture
def expired_paid_user(db):
    user = User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password='testpass123'
    )

    UserProfile.objects.create(
        user=user,
    )

    # expiry date in the past
    UserProfile.objects.create(
        user=user,
        subscription_plan=UserProfile.PAID,
        expires_on=timezone.now() - timezone.timedelta(days=10)
    )

    return user


@pytest.fixture
def free_user_namespace(free_user):
    return Namespace.objects.create(
        user=free_user,
        name='freespace'
    )


@pytest.fixture
def paid_user_namespace(paid_user):
    return Namespace.objects.create(
        user=paid_user,
        name='pr'  # Short namespace for paid user
    )


@pytest.fixture
def shortened_url(free_user_namespace):
    return ShortenedURL.objects.create(
        namespace=free_user_namespace,
        original_url='https://www.example.com',
        shortened_path='test123'
    )