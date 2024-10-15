from django.contrib import admin

from theatre.models import (
    Play,
    Actor,
    TheatreHall,
    Genre,
    Ticket,
    Reservation,
    Performance

)

admin.register(Play)
admin.register(Performance)
admin.register(Actor)
admin.register(TheatreHall)
admin.register(Genre)
admin.register(Ticket)
admin.register(Reservation)
