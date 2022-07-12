from django.db import models

from infra_custom.models.location import Location
from infra_custom.models.product_sku import ProductSku


class StockItem(models.Model):
    sku = models.ForeignKey(
        'infra_custom.ProductSku',
        related_name="stock_items",
        related_query_name="stock_item",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    location = models.ForeignKey(
        'infra_custom.Location',
        related_name="stock_items",
        related_query_name="stock_item",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
