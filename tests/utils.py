from django.db import models
from django.forms.models import model_to_dict


class Person(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    info = models.TextField()


class MockQuerySet(object):
    """
    A class that can take a list of django objects
    that have not actually been saved to a database
    and simulate the methods of a queryset that this
    plugin actually makes use of
    """
    def __init__(self, obj_list):
        self.data = obj_list
        self.model = self.data[0].__class__

    def values(self, *args, **kwargs):
        if args or kwargs:
            raise NotImplementedError("MockQuerySet doesn't support "
                                      "arguments to values.")

        dicts = [model_to_dict(obj) for obj in self.data]
        values_qs = MockQuerySet(dicts)

        if hasattr(self, 'field_names'):
            values_qs.field_names = self.field_names
        else:
            values_qs.field_names = values_qs.data[0].keys()

        return values_qs

    def __repr__(self):
        return repr(self.data)

    def __iter__(self):
        return iter(self.data)
