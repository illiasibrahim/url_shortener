from django.urls import re_path, path
from . import views

urlpatterns = [
    path('home/', views.howe_view, name='home'),

    path('namespace/create/', views.create_namespace, name='create_namespace'),
    path('namespace/list/', views.namespace_list, name='namespace_list'),
    path('namespace/<int:id>/edit/', views.edit_namespace, name='edit_namespace'),
    path('namespace/<int:id>/', views.delete_namespace, name='delete_namespace'),

    path('namespace/<int:namespace_id>/shorten/', views.shorten_url, name='shorten_url'),
    path('urls/list/', views.urls_list, name='urls_list'),
    path('namespace/<int:namespace_id>/urls/<int:url_id>/edit/', views.edit_url, name='edit_url'),
    path('namespace/<int:namespace_id>/urls/<int:url_id>/', views.delete_url, name='delete_url'),
    path('namespace/<int:namespace_id>/urls/<int:url_id>/analytics/', views.url_analytics, name='url_analytics'),
    re_path(r'^(?P<namespace_name>[a-zA-Z0-9_-]+)/(?P<shortened_path>[a-zA-Z0-9_-]+)/$', views.redirect_shortened_url, name='redirect_shortened_url'),
]
