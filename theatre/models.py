import os
import uuid

from django.db import models
from django.template.defaultfilters import slugify


def create_custom_path(instance, filename):
    _, ext = os.path.splitext(filename)
    if isinstance(instance, Play):
        return os.path.join(
            "uploads/images/", f"{slugify(instance.title)}-{uuid.uuid4()}{ext}"
        )
    if isinstance(instance, Actor):
        return os.path.join(
            "uploads/images/", f"{slugify(instance.last_name)}-{uuid.uuid4()}{ext}"
        )


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to=create_custom_path,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        upload_to=create_custom_path,
        null=True,
        blank=True
    )
    actors = models.ManyToManyField(Actor)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title