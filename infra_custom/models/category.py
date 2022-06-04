from django.db import models
from django.core.exceptions import ValidationError

from .attribute import Attribute


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(fields=['parent', 'name'], name='unique_name_for_parent')
        ]
    
    client = models.ForeignKey(
        'infra_auth.Client',
        related_name="categories",
        related_query_name="category",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    name = models.CharField(max_length=64, blank=False, null=False)
    parent = models.ForeignKey(
        'self',
        related_name="children",
        related_query_name="child",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    attributes = models.ManyToManyField(Attribute, through='infra_custom.CategoryAttribute')

    @property
    def full_path(self):
        return self.get_full_path()

    def get_full_path(self):
        return f'{self.parent.get_full_path()} > {self.name}' if self.parent is not None else self.name

    def __str__(self):
        return f'{self.name} ({self.get_full_path()})'

    def get_ancestors(self):
        if self.parent is not None:
            ancestors = self.parent.get_ancestors()
            ancestors.append(self.parent)
            return ancestors
        else:
            return []
    
    # TODO: This may be more efficient by using a "yield" iteration, so as to avoid double iteration (Here and wherever we'd evaluate the values returned here)
    def get_descendants_list(self):
        all_descendants = []
        direct_descendants = self.get_direct_descendants()
        print(f'Descendants for {self.name}: {direct_descendants.values()}')
        all_descendants.extend(direct_descendants)

        for descendant in direct_descendants:
            print(f'Descendant for {self.name}: {descendant.name}')
            indirect_descendants = descendant.get_descendants_list()
            all_descendants.extend(indirect_descendants)
        return all_descendants
    
    def get_direct_descendants(self):
        return Category.objects.filter(parent=self)
    
    def get_siblings(self, **kwargs):
        return Category.objects.exclude(pk=self.pk).filter(parent=self.parent, **kwargs)
    
    # def get_descendants_tree(self) -> if needed, check out LocationLevel

    def save(self, *args, **kwargs):
        if (self.parent is not None) and (self.parent.client != self.client):
            raise ValidationError(f'The parent Category must be of the same client')
        
        if self.get_siblings(name=self.name):
            raise ValidationError(f'A sibling was found with the same name: {self.name}', None, { 'field': 'parent' })

        super(Category, self).save(*args, **kwargs)