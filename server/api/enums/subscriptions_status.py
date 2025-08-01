from django.db import models

class SubscriptionsStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    PENDING = 'pending', 'Pending'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'
    SUSPENDED = 'suspended', 'Suspended'
    TRIAL = 'trial', 'Trial'
    PAUSED = 'paused', 'Paused'
    RENEWAL = 'renewal', 'Renewal'
    FAILED = 'failed', 'Failed'