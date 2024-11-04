from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    FREE = 'free'
    PAID = 'paid'
    SUBSCRIPTION_PLANS = [
        (FREE, 'Free'),
        (PAID, 'Paid'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="user_profiles",
    )
    subscription_plan = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_PLANS,
        default=FREE
    )
    expires_on = models.DateTimeField(blank=True, null=True)

    @property
    def is_paid_user(self):
        return self.subscription_plan == self.PAID
