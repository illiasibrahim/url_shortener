from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import admin

from accounts.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        if obj:
            return super().get_fields(request, obj)
        return ["user"]

    def save_model(self, request, obj, form, change):
        obj.subscription_plan = UserProfile.PAID
        try:
            latest_paid_plan = UserProfile.objects.filter(
                user=obj.user,
                subscription_plan=UserProfile.PAID).latest("id")
        except UserProfile.DoesNotExist:
            latest_paid_plan = None
        start_date = (max(latest_paid_plan.expires_on, datetime.now().astimezone())
                      if latest_paid_plan else datetime.now().astimezone())

        expires_on = start_date + timedelta(
            days=settings.PAID_PLAN_VALIDITY_DAYS
        )
        obj.expires_on = expires_on
        super().save_model(request, obj, form, change)


admin.site.register(UserProfile, UserProfileAdmin)
