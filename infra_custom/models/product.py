from django.db import models
from django.core.exceptions import ValidationError

from .category import Category
from .attribute import Attribute


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        constraints = [
            models.UniqueConstraint(fields=['name', 'brand'], name='unique_name_for_brand')
        ]
    
    client = models.ForeignKey(
        'infra_auth.Client',
        related_name="products",
        related_query_name="product",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    name = models.CharField(max_length=64, blank=False, null=False)
    brand = models.CharField(max_length=64, blank=False, null=False)

    category = models.ForeignKey(
        Category,
        related_name="products",
        related_query_name="product",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    attributes = models.ManyToManyField(Attribute, through='infra_custom.ProductAttribute')

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        return self.get_full_path()
    
    @property
    def category_path(self):
        return self.get_category_path()

    @property
    def related_attributes(self):
        return self.get_all_related_attributes()

    def get_full_path(self):
        return f'{self.category.get_full_path()} > {self.name}'

    def get_category_path(self):
        categories = self.category.get_ancestors()
        categories.append(self.category)
        return categories
    
    def get_all_related_attributes(self):
        # TODO: Most likely not working
        attributes = []
        categories = self.category_path
        for category in categories:
            category_attrs = category.attributes
            attributes.extend(category_attrs)
        return attributes

    def save(self, *args, **kwargs):
        if (self.parent is not None) and (self.category.client != self.client):
            raise ValidationError(f'The Category must be of the same client')
        
        '''
        TODO: If self.attributes.foreach(attr => attr.is_required) -> A default AttributeValue MUST be passed
        '''
        
        '''
        TODO: should manually validate if an ancestor already has a related attribute.
        This scenario should merely continue but provide an "info" formatted message.
        (i.e. This attribute is already appliable in an ancestor category)
        EDGE-CASE: The only exception for this is:
            - that the ancestor's related attribute has is_attribute_required=false AND
            - that the current related attribute is being set to is_attribute_required=true
        '''

        super(Category, self).save(*args, **kwargs)