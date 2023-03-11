from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

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
    attributes = models.ManyToManyField(Attribute, through='infra_custom.ProductAttribute', related_name='products')

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        return self.get_full_path()
    
    @property
    def attributes_qs(self):
        return self.get_all_attributes_qs()

    def get_full_path(self):
        return f'{self.category.get_full_path()} > {self.name}'
    
    def get_all_attributes_qs(self):
        categories = self.category.get_category_path_qs()
        attributes = Attribute.objects.filter(Q(categories__in=list(categories)) | Q(products=self))
        return attributes
    
    def get_attribute_relations_list(self, **kwargs):
        exclude_own_attributes = kwargs.get('exclude_own_attributes')
        attribute_relations = []
        
        categories = self.category.get_category_path_qs()
        category_attrs = Attribute.categories.through.objects.filter(category__in=list(categories))
        attribute_relations.extend(category_attrs)

        if not exclude_own_attributes:
            product_attrs = Attribute.products.through.objects.filter(Q(product=self))
            attribute_relations.extend(product_attrs)

        return attribute_relations

    def save(self, *args, **kwargs):
        if self.category.client != self.client:
            raise ValidationError(f'The Category must be of the same client')

        super(Product, self).save(*args, **kwargs)