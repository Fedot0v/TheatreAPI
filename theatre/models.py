import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.template.defaultfilters import slugify

from TheatreAPIService import settings


def create_custom_path(instance, filename):
    _, ext = os.path.splitext(filename)
    uploads_dir = os.path.join("uploads", "images")

    if isinstance(instance, Play):
        return os.path.join(
            uploads_dir, f"{slugify(instance.title)}-{uuid.uuid4()}{ext}"
        )
    if isinstance(instance, Actor):
        return os.path.join(
            uploads_dir, f"{slugify(instance.last_name)}-{uuid.uuid4()}{ext}"
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
    actors = models.ManyToManyField(
        Actor,
        null=True,
        blank=True,
        related_name="plays"
    )
    genres = models.ManyToManyField(
        Genre,
        null=True,
        blank=True,
        related_name="plays"
    )

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

    def get_taken_seats(self):
        """Returns a list of seats taken by the play"""
        return Ticket.objects.filter(
            performance=self).values_list("row", "seat")

    def get_free_seats(self):
        """Returns a list of free seats for this performance."""
        total_rows = self.theatre_hall.rows
        seats_in_row = self.theatre_hall.seats_in_row
        occupied_seats = set(self.get_taken_seats())

        free_seats = []

        for row in range(1, total_rows + 1):
            for seat in range(1, seats_in_row + 1):
                if (row, seat) not in occupied_seats:
                    free_seats.append((row, seat))
        return free_seats


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

    @staticmethod
    def validate_seat(row, total_rows, seat, num_seats, error_to_raise):
        """Checks if the row and seat is within the valid range."""
        if not (1 <= seat <= num_seats):
            raise error_to_raise(
                {"seat": f"must be in range [1, {num_seats}]"})

        if not (1 <= row <= total_rows):
            raise error_to_raise(
                {"row": f"must be in range [1, {total_rows}]"})

    def clean(self):
        """Checks whether the seat and the row on the ticket is correct,
        based on the total number of seats in the theater hall."""
        total_rows = self.performance.theatre_hall.rows
        seats_in_row = self.performance.theatre_hall.seats_in_row
        Ticket.validate_seat(
            self.row, total_rows, self.seat, seats_in_row, ValidationError
        )

        """Checking if this seat is already booked."""
        if Ticket.objects.filter(
                performance=self.performance,
                row=self.row,
                seat=self.seat,
                reservation__isnull=False,
        ).exists():
            raise ValidationError(
                {"seat": f"Seat {self.seat} in row {self.row} is already booked."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Ticket, self).save(*args, **kwargs)
