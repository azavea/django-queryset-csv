from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=50, verbose_name="Person's name")
    address = models.CharField(max_length=255)
    info = models.TextField(verbose_name="Info on Person")
