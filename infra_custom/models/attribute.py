from django.utils.functional import cached_property
from django.db import models
from django.core.exceptions import ValidationError


class Attribute(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client', 'name'], name='unique_name_for_client')
        ]

    client = models.ForeignKey(
        'infra_auth.Client',
        related_name="attributes",
        related_query_name="attribute",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    name = models.CharField(max_length=64, blank=False, null=False)
    is_value_abbrev_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    