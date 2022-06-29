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
        return self.description
    
    @property
    def related_attributes(self):
        return self.product.attributes_qs

    def get_attribute_values_ids(self):
        return list(map(lambda av : av.id, self.attribute_values.all()))

    def save(self, *args, **kwargs):
        
        '''
        TODO: Check AttributeValues:
        1. All Related Attributes with IsRequired = True MUST Have a Value
        2. All self.attribute_values are values for a Related Attribute. (This needs not raise an exception: but merely filter them)
        '''

        # Dev note:
        # self.attribute_values.through.objects.all() -> Gets you a QS for the through model (ProductSkuAttributeValue)
        # self.attribute_values.all() -> Gets you a QS for the actual related model (AttributeValue)

        '''1. All Related Attributes with IsRequired = True MUST Have a Value'''
        sku_attributes_for_assigned_values = Attribute.objects.filter(attribute_value__id__in=list(map(lambda sav : sav.attributevalue_id, self.attribute_values.through.objects.all())))
        attribute_ids_for_assigned_values = list(map(lambda attr:attr.id, sku_attributes_for_assigned_values))

        product_related_attributes = self.product.get_attribute_relations_list()
        product_related_attribute_ids = list(map(lambda ar : ar.attribute_id, product_related_attributes))

        missing_values_for_attrs = []

        for attribute_rel in product_related_attributes:
            if attribute_rel.is_attribute_required and attribute_rel.attribute_id not in attribute_ids_for_assigned_values:
                attr_name = sku_attributes_for_assigned_values.get(id=attribute_rel.attribute_id).name
                missing_values_for_attrs.append(attr_name)
        if len(missing_values_for_attrs) > 0:
            raise ValidationError(f'A value must be set for the following attributes: {", ".join(missing_values_for_attrs)}', None, { 'field': 'attribute_values' })
        
        '''2. All self.attribute_values are values for a Related Attribute. (This needs not raise an exception: but merely filter them)'''
        self.attribute_values.set(self.attribute_values.filter(attribute_id__in=product_related_attribute_ids).distinct('attribute_id'))

        # missing_attributes_in_product = [attr_id for attr_id in attribute_ids_for_assigned_values if attr_id not in product_related_attribute_ids]
        # if len(missing_attributes_in_product) > 0:
        #     raise ValidationError(f'There are non-assignable attribute values', None, { 'field': 'attribute_values' })

        '''
        TODO: Check for duplicates of possible RelatedAttributes combinations 
        So something like a foreach val in attribute_values: ProductSku.object.filter(attribute_values__icontains??=val)
        '''
        self_attr_value_ids = self.get_attribute_values_ids()

        existing_product_skus = ProductSku.objects.filter(product=self.product).exclude(id=self.id)
        existing_skus_attribute_values_ids = list(map(lambda sku : sku.get_attribute_values_ids(), existing_product_skus))

        for sku_attr_value_ids in existing_skus_attribute_values_ids:
            if len(set(sku_attr_value_ids).symmetric_difference(set(self_attr_value_ids))) == 0:
                raise ValidationError(f'Another SKU for the same Product has the exact same attribute values.', None, { 'field': 'attribute_values' })

        super(ProductSku, self).save(*args, **kwargs)