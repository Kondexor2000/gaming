from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Laptop(models.Model):
    owner = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    cale = models.FloatField()
    price = models.FloatField()
    processor = models.IntegerField()
    graphics_card = models.IntegerField()
    ram = models.IntegerField()
    rom = models.IntegerField()
    url = models.TextField()
