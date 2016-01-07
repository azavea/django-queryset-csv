from django.db import models

from django.utils.translation import ugettext as _

from datetime import datetime

SOME_TIME = datetime(2001, 1, 1, 1, 1)


class Activity(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name of Activity")


class Person(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Person's name"))
    address = models.CharField(max_length=255)
    info = models.TextField(verbose_name="Info on Person")
    hobby = models.ForeignKey(Activity)
    born = models.DateTimeField(default=SOME_TIME)

    def __unicode__(self):
        return self.name
