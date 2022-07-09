from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from ..models.product_sku import ProductSku, Attribute, AttributeValue


@receiver(m2m_changed, sender=ProductSku.attribute_values.through, weak=False, dispatch_uid="product_sku__add_attribute_value")
def add_attribute_value_to_product_sku(sender, **kwargs):
    if 1 == 1:
        return
    
    # Do something
    print(f'sender: ', sender)
    print(kwargs)

    action = kwargs.pop('action')
    if action == 'pre_add' or action == 'pre_remove':
        is_valid = True

        instance = kwargs.pop('instance')
        # BELOW should be something like: else list(map(lambda attr_val : attr_val.id, instance.attribute_values.all())) MINUS kwargs.pop('pk_set')
        # SO something like "All the current attributes MINUS the ones we're removing" those are supposed the ones to remain
        # Quite some edge cases here.
        attribute_value_ids = kwargs.pop('pk_set') if action == 'pre_add' else list(map(lambda attr_val : attr_val.id, instance.attribute_values.all()))
        attribute_values = AttributeValue.objects.filter(id__in=attribute_value_ids)
        print('instance: ', instance)
        print('attribute_value_ids: ', attribute_value_ids)
        print('attribute_values: ', attribute_values)

        '''1. All Related Attributes with [IsRequired = True] MUST Have a Value'''
        attributes = Attribute.objects.filter(attribute_value__id__in=list(map(lambda attr_val : attr_val.id, attribute_values)))
        attribute_ids = list(map(lambda attr:attr.id, attributes))
        print('attributes: ', attributes)
        print('attribute_ids: ', attribute_ids)

        print('instance.product: ', instance.product)
        product_category_attributes = instance.product.get_attribute_relations_list()
        product_category_attribute_ids = list(map(lambda ar : ar.attribute_id, product_category_attributes))

        print('product_category_attributes: ', product_category_attributes)
        print('product_category_attribute_ids: ', product_category_attribute_ids)

        missing_values_for_attrs = []

        for attribute_rel in product_category_attributes:
            if attribute_rel.is_attribute_required and attribute_rel.attribute_id not in attribute_ids:
                # attr_name = sku_attribute_values.get(id=attribute_rel.attribute_id).name
                attr_name = Attribute.objects.get(id=attribute_rel.attribute_id).name
                missing_values_for_attrs.append(attr_name)
        if len(missing_values_for_attrs) > 0:
            # raise ValidationError(f'A value must be set for the following attributes: {", ".join(missing_values_for_attrs)}', None, { 'field': 'attribute_values' })
            is_valid = False
        print('missing_values_for_attrs', missing_values_for_attrs)

        '''2. All self.attribute_values are values for a Related Attribute. (This needs not raise an exception: but merely filter them: Can't do that!)'''
        # valid_attribute_values = attribute_values.filter(attribute_id__in=product_category_attribute_ids)
        # if len(valid_attribute_values) != len(attribute_values):
        #     raise ValidationError(f'There are values set for an attribute not related to this SKU', None, { 'field': 'attribute_values' })
        missing_attributes_in_product = [attr_id for attr_id in attribute_ids if attr_id not in product_category_attribute_ids]
        if len(missing_attributes_in_product) > 0:
            is_valid = False
            # raise ValidationError(f'There are non-assignable attribute values', None, { 'field': 'attribute_values' })
        
        valid_attribute_values = attribute_values.distinct('attribute_id')
        if len(valid_attribute_values) != len(attribute_values):
            is_valid = False
            # raise ValidationError(f'There are duplicate values for a single attribute.', None, { 'field': 'attribute_values' })
        
        '''
        TODO: Check for duplicates of possible RelatedAttributes combinations 
        So something like a foreach val in attribute_values: ProductSku.object.filter(attribute_values__icontains??=val)
        '''
        existing_product_skus = ProductSku.objects.filter(product=instance.product).exclude(id=instance.id)
        existing_skus_attribute_values_ids = list(map(lambda sku : sku.get_attribute_values_ids(), existing_product_skus))

        for sku_attr_value_ids in existing_skus_attribute_values_ids:
            if len(set(sku_attr_value_ids).symmetric_difference(set(attribute_value_ids))) == 0:
                is_valid = False
                # raise ValidationError(f'Another SKU for the same Product has the exact same attribute values.', None, { 'field': 'attribute_values' })
        
        print('is_valid', is_valid)
        instance.is_valid = is_valid
        instance.save()






# m2m_changed.connect(add_attribute_value_to_product_sku, sender=ProductSku.attribute_values.through, weak=False, dispatch_uid="product_sku__add_attribute_value")