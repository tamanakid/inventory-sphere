from django.db import models
from django.core.exceptions import ValidationError

from .attribute import Attribute
from .category import Category
from .product import Product

class CategoryAttribute(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    is_attribute_required = models.BooleanField(default=True)


class ProductAttribute(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    is_attribute_required = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # This is only called by the admin code. The API has its own implementation to verify this
        for attribute_rel in self.product.get_attribute_relations_list(exclude_own_attributes=True):
            print(f'{attribute_rel.attribute} - {attribute_rel.is_attribute_required}')
            if (attribute_rel.attribute == self.attribute):
                return

        super(ProductAttribute, self).save(*args, **kwargs)
