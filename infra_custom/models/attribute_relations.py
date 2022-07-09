from django.db import models
from django.core.exceptions import ValidationError

from .attribute import Attribute
from .category import Category
from .product import Product

class CategoryAttribute(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    is_attribute_required = models.BooleanField(default=True)

    # TODO: Once Products/SKUs are developed:
    # If is_attribute_required == True
    # Check all Products of self.category and all its children categories that are associated to self.attribute
    # If said Products' SKUs don't have a value for the attribute:
    # either throw an error or assign a default value? (Or both)



class ProductAttribute(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    is_attribute_required = models.BooleanField(default=True)

    # TODO: Once Products/SKUs are developed:
    # If is_attribute_required == True
    # Check all Products of self.category and all its children categories that are associated to self.attribute
    # If said Products' SKUs don't have a value for the attribute:
    # either throw an error or assign a default value? (Or both)

    def save(self, *args, **kwargs):       
        '''
        TODO: should manually validate if an ancestor already has a related attribute.
        This scenario should merely continue but provide an "info" formatted message.
        (i.e. This attribute is already appliable in an ancestor category)
        EDGE-CASE: The only exception for this is:
            - that the ancestor's related attribute has is_attribute_required=false AND
            - that the current related attribute is being set to is_attribute_required=true
        '''
        # NOTE: This is only called by the admin code. The API has its own implementation to verify this
        for attribute_rel in self.product.get_attribute_relations_list(exclude_own_attributes=True):
            print(f'{attribute_rel.attribute} - {attribute_rel.is_attribute_required}')
            if (attribute_rel.attribute == self.attribute):
                return

        super(ProductAttribute, self).save(*args, **kwargs)
