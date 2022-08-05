from datetime import *
from django.db import models
from django.contrib.auth.models import AbstractUser

from infra_auth.managers import UserManager
from infra_custom.models.location import Location


class User(AbstractUser):

    # Permission Roles
    class Role(models.TextChoices):
        INVENTORY_MANAGER = 'IM', 'Inventory Manager'
        STORAGE_MANAGER = 'SM', 'Storage Manager'
        STORAGE_EMPLOYEE = 'SE', 'Storage Employee'
        DATA_EMPLOYEE = 'DE', 'Data Employee'
    
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField(blank=False, null=False, max_length=32)
    last_name = models.CharField(blank=False, null=False, max_length=32)
    last_password_change = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    client = models.ForeignKey(
        'infra_auth.Client',
        related_name="users",
        related_query_name="user",
        on_delete=models.CASCADE,
        null=True,
    )
    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.STORAGE_EMPLOYEE,
    )
    locations = models.ManyToManyField(Location, through='infra_auth.UserLocation', related_name='users', related_query_name='user')
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Manager
    objects = UserManager()

    def __str__(self):
        return self.email
    
    def is_storage_user(self):
        return self.role == User.Role.STORAGE_MANAGER or self.role == User.Role.STORAGE_EMPLOYEE

    def save(self, *args, **kwargs):
        if not self.is_superuser and not self.is_staff and (self.client is None):
            raise ValueError('Regular users must be associated to an existing Client')

        if (self.client is not None) and (self.is_superuser == True or self.is_staff == True):
            raise ValueError('Regular users associated to a Client cannot have superuser or staff access')

        super(User, self).save(*args, **kwargs)
    
    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.last_password_change = datetime.now()
