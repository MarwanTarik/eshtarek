from django.db import models

class SubscriptionsBillingCycle(models.TextChoices):
    MONTHLY = 'monthly', 'Monthly'
    ANNUALLY = 'annually', 'Annually'