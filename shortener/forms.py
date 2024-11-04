# shortener/forms.py
import re

from django import forms
from django.conf import settings

from .constants import PAID_USER_NAME_MIN_LENGTH, FREE_USER_NAME_MIN_LENGTH
from .models import Namespace, ShortenedURL


class NamespaceForm(forms.ModelForm):
    class Meta:
        model = Namespace
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_profile = self.user.user_profiles.latest("id")
        super().__init__(*args, **kwargs)

    def get_name_space_limit(self):
        if self.user_profile.is_paid_user:
            return settings.PAID_USER_NAMESPACE_LIMIT
        return settings.FREE_USER_NAMESPACE_LIMIT

    def get_name_min_length(self):
        if self.user_profile.is_paid_user:
            return PAID_USER_NAME_MIN_LENGTH
        return FREE_USER_NAME_MIN_LENGTH

    def clean_name(self):
        name = self.cleaned_data.get("name")
        name_min_length = self.get_name_min_length()
        pattern = r'^[a-z0-9]{%s,}$' % name_min_length

        if not re.match(pattern, name):
            raise forms.ValidationError(
                f"This field can only contain lowercase letters "
                f"and numbers, with at least {name_min_length} characters.")
        if Namespace.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(
                "This namespace is already been taken."
            )
        return name

    def clean(self):
        cleaned_data = super().clean()
        name_space_limit = self.get_name_space_limit()
        if Namespace.objects.filter(user=self.user).exclude(id=self.instance.id).count() >= name_space_limit:
            raise forms.ValidationError("You have reached maximum namespace limit.")
        return cleaned_data


class ShortenURLForm(forms.ModelForm):
    keyword = forms.CharField(
        required=False,  # Make the keyword optional
        help_text="Optional: Enter a custom keyword for the shortened URL."
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.namespace = kwargs.pop('namespace', None)
        self.user_profile = self.user.user_profiles.latest("id")
        super().__init__(*args, **kwargs)

    def get_urls_limit(self):
        if self.user_profile.is_paid_user:
            return settings.PAID_USER_URLS_LIMIT
        return settings.FREE_USER_URLS_LIMIT

    def clean_keyword(self):
        keyword = self.cleaned_data.get("keyword")
        if keyword:
            pattern = r'^[a-z0-9]{1,5}$'

            if not re.match(pattern, keyword):
                raise forms.ValidationError(
                    f"This field can only contain lowercase letters "
                    f"and numbers, within the range of 1 to 5 characters")
        return keyword

    def clean(self):
        cleaned_data = super().clean()
        urls_limit = self.get_urls_limit()
        if ShortenedURL.objects.filter(
                namespace__user=self.user).exclude(
                id=self.instance.id).count() >= urls_limit:
            raise forms.ValidationError(f"You have reached maximum URLs limit of {urls_limit}.")
        return cleaned_data

    class Meta:
        model = ShortenedURL
        fields = ['original_url', 'keyword']
