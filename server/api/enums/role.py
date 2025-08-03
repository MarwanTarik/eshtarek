from django.db import models

class Role(models.TextChoices):
    TENANT_ADMIN = 'tenant_admin', 'Tenant Admin'
    TENANT_USER = 'tenant_user', 'Tenant User'
    PLATFORM_ADMIN = 'platform_admin', 'Platform Admin'