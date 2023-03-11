from django.db import models
from django.utils.functional import cached_property

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
    is_valid = models.BooleanField(default=False)

    @cached_property
    def client(self):
        return self.product.client

    def __str__(self):
        return self.description
    
    @property
    def related_attributes(self):
        return self.product.attributes_qs

    def get_attribute_values_ids(self):
        return list(map(lambda av : av.id, self.attribute_values.all()))
    
    def save(self, *args, **kwargs):        
        super(ProductSku, self).save(*args, **kwargs)
        print(self.pk)