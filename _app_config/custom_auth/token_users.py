from django.utils.functional import cached_property
from rest_framework_simplejwt.models import TokenUser

from infra_auth import models as infra_auth


class CustomTokenUser(TokenUser):
    @cached_property
    def client_id(self):
        return self.token.get("client_id", "")
