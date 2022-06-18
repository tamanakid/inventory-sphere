from django.db import models
from django.core.exceptions import ValidationError

from .category import Category
from .attribute import Attribute
from .attribute_value import AttributeValue
from .product import Product



class ProductSku(models.Model):
    class Meta:
        verbose_name = "SKU"
        verbose_name_plural = "SKUs"
        constraints = [
            models.UniqueConstraint(fields=['description', 'product'], name='unique_description_for_product')
        ]
    
    product = models.ForeignKey(
        Product,
        related_name="skus",
        related_query_name="sku",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    description = models.CharField(max_length=256, blank=False, null=False)
    attribute_values = models.ManyToManyField(AttributeValue, related_name='skus', related_query_name='sku')

    def __str__(self):
        return self.name
    
    @property
    def related_attributes(self):
        return self.product.get_all_related_attributes()

    def save(self, *args, **kwargs):
        '''
        TODO: Check AttributeValues:
        1. All Related Attributes with IsRequired = True MUST Have a Value
        2. All self.attribute_values are values for a Related Attribute.
        '''

        '''
        TODO: Check for duplicates of possible RelatedAttributes combinations 
        So something like a foreach val in attribute_values: ProductSku.object.filter(attribute_values__icontains??=val)
        '''

        super(Category, self).save(*args, **kwargs)