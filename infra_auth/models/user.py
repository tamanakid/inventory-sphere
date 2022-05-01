from django.db import models
from django.contrib.auth.models import AbstractUser

from infra_auth.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField(blank=False, null=False, max_length=32)
    last_name = models.CharField(blank=False, null=False, max_length=32)
    client = models.ForeignKey(
        'infra_auth.Client',
        related_name="users",
        related_query_name="user",
        on_delete=models.CASCADE,
        null=True,
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Manager
    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.is_superuser and not self.is_staff and (self.client is None):
            raise ValueError('Regular users must be associated to an existing Client')

        if (self.client is not None) and (self.is_superuser == True or self.is_staff == True):
            raise ValueError('Regular users associated to a Client cannot have superuser or staff access')

        super(User, self).save(*args, **kwargs)