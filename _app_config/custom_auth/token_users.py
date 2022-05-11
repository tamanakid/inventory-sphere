from django.db.models.manager import EmptyManager
from rest_framework_simplejwt.models import TokenUser

from infra_auth import models as infra_auth


class CustomTokenUser(TokenUser):
    pass
    # _client = EmptyManager(infra_auth.Client)

    # @property
    # def client(self):
    #     return self._client
