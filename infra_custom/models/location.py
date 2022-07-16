from django.utils.functional import cached_property
from django.db import models
from django.core.exceptions import ValidationError

from utils.data_types import get_roman_numeric_from_integer, get_alphabet_index_from_integer


class Location(models.Model):
    class Meta:
        ordering = ['-id']

    # Indexing for creational pattern (Not for data storage layer)
    class StructureIndexType(models.TextChoices):
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
    
    def get_parents_qs(self):
        if self.parent is None:
            return Location.objects.none()
        else:
            parents_qs = self.parent.get_parents_qs()
            parents_qs |= Location.objects.filter(id=self.parent.id)
            return parents_qs
    
    def get_all_descendants_qs(self, level_locations_qs=None):
        if level_locations_qs is None:
            level_locations_qs = Location.objects.filter(id=self.id)
        direct_descendants_qs = Location.objects.filter(parent__in=level_locations_qs)
        # This would happen when reaching the last level of Location "children"
        if direct_descendants_qs.count() == 0:
            return level_locations_qs
        # This returns all children found below, plus the ones found in this level
        return self.get_all_descendants_qs(direct_descendants_qs) | level_locations_qs


    def __str__(self):
        return self.get_full_path()

    def get_siblings(self, **kwargs):
        return Location.objects.filter(parent=self.parent, **kwargs)

    def save(self, *args, **kwargs):
        if self.parent is not None:
            if self.level.parent != self.parent.level:
                raise ValidationError('The Level selected does not match the Parent selected')
        else:
            if self.level.parent is not None:
                raise ValidationError('A Location in the selected Level must have a parent Location')
        
        if self.get_siblings(name=self.name):
            raise ValidationError(f'A sibling was found with the same name: {self.name}', None, { 'field': 'parent' })

        super(Location, self).save(*args, **kwargs)
    
    def is_inside_rsl(self):
        return False if self.parent is None else (self.parent.level.is_root_storage_level or self.parent.is_inside_rsl())

    @classmethod
    def get_location_index(cls, i, index_type):
        if index_type == cls.StructureIndexType.ALPHABETIC:
            return get_alphabet_index_from_integer(i)
        elif index_type == cls.StructureIndexType.ROMAN:
            return get_roman_numeric_from_integer(i+1)
        elif index_type == cls.StructureIndexType.DECIMAL_1:
            return i + 1
        return i
