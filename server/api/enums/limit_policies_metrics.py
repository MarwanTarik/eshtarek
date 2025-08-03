from django.db import models

class LimitPoliciesMetrics(models.TextChoices):
    MAX_USERS = 'max_users', 'Max Users'