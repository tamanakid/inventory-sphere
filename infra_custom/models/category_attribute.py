from django.db import models
from django.core.exceptions import ValidationError

from .attribute import Attribute
from .category import Category


class CategoryAttribute(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    is_attribute_required = models.BooleanField(default=True)

    # TODO: Once Products/SKUs are developed:
    # If is_attribute_required == True
    # Check all Products of self.category and all its children categories that are associated to self.attribute
    # If said Products' SKUs don't have a value for the attribute:
    # either throw an error or assign a default value? (Or both)