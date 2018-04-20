from django.db import models

from django.utils.translation import ugettext as _
from django.utils.encoding import python_2_unicode_compatible
from datetime import datetime

SOME_TIME = datetime(2001, 1, 1, 1, 1)


class Activity(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name of Activity")


@python_2_unicode_compatible
class Person(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Person's name"))
    address = models.CharField(max_length=255)
    info = models.TextField(verbose_name="Info on Person")
    hobby = models.ForeignKey(Activity, on_delete=models.CASCADE)
    born = models.DateTimeField(default=SOME_TIME)

    def __str__(self):
        return self.name
