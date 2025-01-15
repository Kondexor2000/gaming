from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Store(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} owned by {self.user.username}"

class Laptop(models.Model):
    owner = models.ManyToManyField(Store)  # Corrected ManyToManyField
    name = models.CharField(max_length=255)
    screen_size = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    processor = models.IntegerField()
    graphics_card = models.IntegerField()
    ram = models.IntegerField()
    storage = models.PositiveIntegerField()  # Ensure this is an integer field
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)  # DateTimeField
    updated_at = models.DateTimeField(auto_now=True)  # DateTimeField

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='reviews')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.laptop.name}"