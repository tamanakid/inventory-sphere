from datetime import *
from django.db import models

from infra_auth.models.user import User
from infra_custom.models.location import Location


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.user.client == self.location.level.client:
            return

        # NOTE: This is only called by the admin code. The API has its own implementation to verify this
        if not self.user.is_storage_user:
            return
        
        '''
        user_locations = self.user.locations.through.objects.filter(user=self.user)
        '''
        super(UserLocation, self).save(*args, **kwargs)