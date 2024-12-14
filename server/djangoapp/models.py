from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)  # Optional description
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set on every update
    
    def __str__(self):
        return self.name  # Return the name as the string representation

    class Meta:
        ordering = ['name']  # Optionally, you can add ordering by name

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, related_name='models', on_delete=models.CASCADE)  # Many-to-One relationship
    name = models.CharField(max_length=100)
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        ('COUPE', 'Coupe'),
        ('CONVERTIBLE', 'Convertible'),
        # Add more car types as needed
    ]
    type = models.CharField(max_length=12, choices=CAR_TYPES, default='SUV')
    year = models.IntegerField(default=2023,
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ])
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set on every update
    
    def __str__(self):
        return f"{self.name} ({self.car_make.name})"  # Return the model name and the associated make

    class Meta:
        ordering = ['name']  # Optionally, you can add ordering by model name

