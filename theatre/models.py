import os
import uuid

from django.db import models
from django.db.models import UniqueConstraint
from django.template.defaultfilters import slugify

from TheatreAPIService import settings


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


class TheatreHall(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return self.name


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class Performance(models.Model):
    play: Play = models.ForeignKey(
        Play,
        on_delete=models.CASCADE,
        related_name="performances",
    )
    theatre_hall: TheatreHall = models.ForeignKey(
        TheatreHall,
        on_delete=models.CASCADE,
        related_name="performances",
    )
    show_time = models.DateTimeField()

    def __str__(self):
        return (f"{self.play}."
                f" Theatre hall: {self.theatre_hall}."
                f" Show time: {self.show_time}"
        )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "performance"],
                name="unique_ticket"
            )
        ]

    def __str__(self):
        return f"{self.performance}. Seat: {self.seat}, row: {self.row}"
