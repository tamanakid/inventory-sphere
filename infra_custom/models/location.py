from django.utils.functional import cached_property
from django.db import models
from django.core.exceptions import ValidationError


class Location(models.Model):

    # Indexing for creational pattern (Not for data storage layer)
    class StuctureIndex(models.TextChoices):
        ALPHABETIC = 'AL', 'Alphabetically (A, B, C, ..Z, AA...)'
        ROMAN = 'RO', 'Roman Numeric (I, II, III...)'
        DECIMAL_1 = 'D1', 'Decimal from 1 (1, 2, 3...)'
        DECIMAL_0 = 'D0', 'Decimal from 0 (0, 1, 2, 3...)'


    name = models.CharField(max_length=64, blank=False, null=False)
    parent = models.ForeignKey(
        'self',
        related_name="children",
        related_query_name="child",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    level = models.ForeignKey(
        'infra_custom.LocationLevel',
        related_name="locations",
        related_query_name="location",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    @cached_property
    def client(self):
        return self.level.client

    @property
    def full_path(self):
        return self.get_full_path()

    def get_full_path(self):
        return f'{self.parent.get_full_path()} > {self.name}' if self.parent is not None else self.name

    def __str__(self):
        return self.get_full_path()

    def save(self, *args, **kwargs):
        if self.parent is not None:
            if self.level.parent != self.parent.level:
                raise ValidationError('The Level selected does not match the Parent selected')
        else:
            if self.level.parent is not None:
                raise ValidationError('A Location in the selected Level must have a parent Location')

        super(Location, self).save(*args, **kwargs)