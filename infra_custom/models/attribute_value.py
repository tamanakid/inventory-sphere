from django.utils.functional import cached_property
from django.db import models
from django.core.exceptions import ValidationError


class AttributeValue(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['attribute', 'name'], name='unique_name_for_attribute'),
            models.UniqueConstraint(fields=['attribute', 'abbreviation'], name='unique_abbrev_for_attribute')
        ]

    attribute = models.ForeignKey(
        'infra_custom.Attribute',
        related_name="attribute_values",
        related_query_name="attribute_value",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    name = models.CharField(max_length=64, blank=False, null=False)
    abbreviation = models.CharField(max_length=3, blank=True, null=True)

    @cached_property
    def client(self):
        return self.attribute.client
    

    def save(self, *args, **kwargs):
        if self.attribute.is_value_abbrev_required:
            if self.abbreviation is None or len(self.abbreviation) == 0:
                raise ValidationError(f'Values for Attribute "{self.attribute.name}" must have an Abbreviation', None, { 'field': 'abbreviation' })
        
        super(AttributeValue, self).save(*args, **kwargs)