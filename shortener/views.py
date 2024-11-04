# shortener/views.py
import string
import random

from datetime import datetime

from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Namespace, ShortenedURL, URLAccessLog
from .forms import NamespaceForm, ShortenURLForm


@login_required
def create_namespace(request):
    if request.method == 'POST':
        form = NamespaceForm(request.POST, user=request.user)
        if form.is_valid():
            namespace = form.save(commit=False)
            namespace.user = request.user
            namespace.save()
            return redirect('namespace_list')
    else:
        form = NamespaceForm(user=request.user)
    return render(
        request,
        'namespace/edit_namespace.html',
        {'form': form}
    )

@login_required
def namespace_list(request):
    # Fetch all namespaces created by the logged-in user
    namespaces = Namespace.objects.filter(user=request.user)
    return render(
        request,
        'namespace/namespace_list.html',
        {'namespaces': namespaces}
    )


@login_required
def howe_view(request):
    return render(request, "home.html")


@login_required
def edit_namespace(request, id):
    namespace = get_object_or_404(
        Namespace, id=id, user=request.user
    )

    if request.method == 'POST':
        form = NamespaceForm(
            request.POST,
            instance=namespace,
            user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect('namespace_list')
    else:
        form = NamespaceForm(
            instance=namespace,
            user=request.user
        )

    return render(
        request,
        'namespace/edit_namespace.html',
        {'form': form, 'namespace': namespace}
    )


@login_required
def delete_namespace(request, id):
    namespace = get_object_or_404(Namespace, id=id, user=request.user)

    if request.method == 'POST':
        namespace.delete()
        return redirect('namespace_list')

    return render(
        request,
        'namespace/confirm_delete.html',
        {'namespace': namespace}
    )


def generate_random_string():
    length = random.randint(1, 5)
    characters = string.ascii_letters + string.digits
    random_string = ''.join(
        random.choice(characters) for _ in range(length)
    )
    return random_string


@login_required
def shorten_url(request, namespace_id):
    namespace = get_object_or_404(
        Namespace, id=namespace_id, user=request.user
    )
    if request.method == 'POST':
        form = ShortenURLForm(
            request.POST, user=request.user
        )
        if form.is_valid():
            url = form.save(commit=False)
            url.namespace = namespace
            keyword = form.cleaned_data.get("keyword")
            if keyword:
                shortened_path = keyword
            else:
                shortened_path = generate_random_string()
            while ShortenedURL.objects.filter(
                    namespace=namespace,
                    shortened_path=shortened_path).exists():
                shortened_path = keyword + generate_random_string()
            url.shortened_path = shortened_path
            url.save()
            return redirect('home')
    else:
        form = ShortenURLForm(user=request.user)
    return render(
        request,
        'url/edit_shorten_url.html',
        {'form': form, 'namespace': namespace}
    )


def redirect_shortened_url(request, namespace_name, shortened_path):
    try:
        namespace = Namespace.objects.get(name=namespace_name)
        user = namespace.user
        latest_user_profile = user.user_profiles.latest("id")
        if latest_user_profile.is_paid_user:
            now = datetime.now().astimezone()
            has_permission = now <= latest_user_profile.expires_on
        else:
            has_permission = True
        assert has_permission
        shortened_url = ShortenedURL.objects.get(
            namespace=namespace, shortened_path=shortened_path
        )

        return redirect(shortened_url.original_url)
    except (
            Namespace.DoesNotExist,
            ShortenedURL.DoesNotExist,
            AssertionError,
    ):
        raise Http404("Shortened URL not found.")


@login_required
def urls_list(request):
    # Fetch all urls created by the logged-in user
    urls = ShortenedURL.objects.filter(namespace__user=request.user)
    for url in urls:
        url.full_short_url = url.get_shortened_url(request)
    return render(
        request,
        'url/url_list.html',
        {'urls': urls}
    )


@login_required
def edit_url(request, namespace_id, url_id):
    namespace = get_object_or_404(
        Namespace, id=namespace_id, user=request.user
    )
    url = get_object_or_404(
        ShortenedURL, id=url_id, namespace=namespace
    )

    if request.method == 'POST':
        form = ShortenURLForm(
            request.POST, instance=url, user=request.user
        )
        if form.is_valid():
            url = form.save(commit=False)
            keyword = form.cleaned_data.get("keyword")
            if keyword:
                shortened_path = keyword
            else:
                shortened_path = generate_random_string()
            while ShortenedURL.objects.filter(
                    namespace=namespace,
                    shortened_path=shortened_path).exists():
                shortened_path = keyword + generate_random_string()
            url.shortened_path = shortened_path
            url.save()
            return redirect('urls_list')
    else:
        form = ShortenURLForm(user=request.user, instance=url)
    return render(
        request,
        'url/edit_shorten_url.html',
        {'form': form, 'namespace': namespace}
    )


@login_required
def delete_url(request, namespace_id, url_id):
    namespace = get_object_or_404(
        Namespace, id=namespace_id, user=request.user
    )
    url = get_object_or_404(
        ShortenedURL, id=url_id, namespace=namespace
    )

    if request.method == 'POST':
        url.delete()
        return redirect('urls_list')

    return render(
        request,
        'url/confirm_delete.html',
        {'url': url}
    )


def url_analytics(request, namespace_id, url_id):
    # Ensure the URL belongs to the user and matches the namespace
    url = get_object_or_404(
        ShortenedURL,
        id=url_id,
        namespace=namespace_id,
        namespace__user=request.user,
    )

    # Get most common location
    most_common_location = (
        URLAccessLog.objects.filter(url=url)
        .values('city', 'region', 'country')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    # Get top 5 locations
    top_locations = (
        URLAccessLog.objects.filter(url=url)
        .values('city', 'region', 'country')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    context = {
        'url': url,
        'most_common_location': most_common_location,
        'top_locations': top_locations,
    }
    return render(request, 'url/analytics.html', context)
