from django.db import models


class Event(models.Model):
    name = models.TextField()
    date = models.DateField()
    place = models.CharField(max_length=30)
    organizer = models.CharField(max_length=30)
    description = models.TextField()
    price = models.CharField(max_length=30)
    tags = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True)
