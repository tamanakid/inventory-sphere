from django.db import models
from django.core.exceptions import ValidationError


class LocationLevel(models.Model):
    client = models.ForeignKey(
        'infra_auth.Client',
        related_name="location_levels",
        related_query_name="location_level",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    name = models.CharField(max_length=64, blank=False, null=False)
    is_root_storage_level = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        related_name="children",
        related_query_name="child",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    @property
    def full_path(self):
        return self.get_full_path()

    def get_full_path(self):
        return f'{self.parent.get_full_path()} > {self.name}' if self.parent is not None else self.name

    def __str__(self):
        return self.get_full_path()

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
        direct_descendants = LocationLevel.objects.exclude(parent=None).filter(parent=self)
        print(f'Descendants for {self.name}: {direct_descendants.values()}')
        all_descendants.extend(direct_descendants)

        for descendant in direct_descendants:
            print(f'Descendant for {self.name}: {descendant.name}')
            indirect_descendants = descendant.get_descendants_list()
            all_descendants.extend(indirect_descendants)
        return all_descendants

    def get_direct_descendants(self):
        return LocationLevel.objects.filter(parent=self)
    
    def get_siblings(self, **kwargs):
        return LocationLevel.objects.filter(parent=self.parent, **kwargs)

    # Returns a list with direct descendants, with all nested descendants within
    # https://stackoverflow.com/a/29088221/8417780
    def get_descendants_tree(self):
        direct_descendants = self.get_direct_descendants()
        for descendant in direct_descendants:
            descendant_dict = self.__dict__
            descendant_dict['children'] = list(descendant.get_descendants_tree())
        return direct_descendants


    def save(self, *args, **kwargs):
        if (self.parent is not None) and (self.parent.client != self.client):
            raise ValidationError(f'The parent LocationLevel must be of the same client')
        
        if self.get_siblings(name=self.name):
            raise ValidationError(f'A sibling was found with the same name: {self.name}', None, { 'field': 'parent' })
            # raise ValidationError(f'A sibling was found with the same name: {self.name}') -> Example of _root error
        
        if self.is_root_storage_level:
            print('Checking if ancestors or descendants already have User Scope...')
            ancestors = self.get_ancestors()
            for ancestor in ancestors:
                if ancestor.is_root_storage_level:
                    raise ValidationError(f'Another ancestor Level already has User Scope: {ancestor.name}', None, { 'field': 'is_root_storage_level' })

            descendants = self.get_descendants_list()
            for descendant in descendants:
                if descendant.is_root_storage_level:
                    raise ValidationError(f'Another descendant Level already has User Scope: {descendant.name}', None, { 'field': 'is_root_storage_level' })

        super(LocationLevel, self).save(*args, **kwargs)
