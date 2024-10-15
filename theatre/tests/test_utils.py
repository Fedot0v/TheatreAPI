import uuid
from datetime import datetime, timedelta

from theatre.models import Play, Actor, Genre, TheatreHall, Performance, Reservation, Ticket


def sample_play(**params):
    defaults = {
        "title": f"Test play {uuid.uuid4()}",
        "description": "Test play",
        "image": params.get("image", None)
    }
    defaults.update(params)
    return Play.objects.create(**defaults)


def sample_actor(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
        "image": params.get("image", None)
    }
    defaults.update(params)
    return Actor.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": f"Test genre {uuid.uuid4()}",
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


def sample_theatre_hall(**params):
    defaults = {
        "name": "Test Hall",
        "rows": 6,
        "seats_in_row": 15
    }
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def sample_performance(
        play=None,
        theatre_hall=None,
        show_time=None,
        **params
):
    if play is None:
        play = sample_play(**params)
    if theatre_hall is None:
        theatre_hall = sample_theatre_hall(**params)
    if show_time is None:
        show_time = datetime.now() + timedelta(days=1)

    defaults = {
        "play": play,
        "theatre_hall": theatre_hall,
        "show_time": show_time,
    }
    defaults.update(params)
    return Performance.objects.create(**defaults)


def sample_reservation(user, performance=None, **params):
    if performance is None:
        performance = sample_performance(**params)

    reservation = Reservation.objects.create(user=user)

    tickets = params.pop('tickets', [])
    for ticket_data in tickets:
        Ticket.objects.create(
            row=ticket_data['row'],
            seat=ticket_data['seat'],
            performance=performance,
            reservation=reservation,
        )

    return reservation


def sample_ticket(
        row=5,
        seat=10,
        performance=None,
        reservation=None,
        **params
):
    if performance is None:
        performance = sample_performance(**params)

    if reservation is None:
        reservation = sample_reservation(
            user=params.get('user'),
            performance=performance
        )

    defaults = {
        "row": row,
        "seat": seat,
        "performance": performance,
        "reservation": reservation,
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)
