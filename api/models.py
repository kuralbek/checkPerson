from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=450)
    iin = models.CharField(max_length=12)
    phone = models.CharField(max_length=12)
