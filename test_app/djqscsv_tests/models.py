from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    info = models.TextField()
