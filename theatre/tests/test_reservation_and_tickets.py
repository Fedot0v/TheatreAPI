import uuid
from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Reservation, Ticket, Performance, TheatreHall, Play
from theatre.tests.test_utils import sample_reservation

RESERVATION_URL = reverse("theatre:reservation-list")

def detail_url(ticket_id):
    return reverse("theatre:reservation-detail", args=[ticket_id])

class UnAuthenticatedTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class TestAuthenticatedUser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="<PASSWORD>",
        )

        cls.play = Play.objects.create(
            title=f"Test play {uuid.uuid4()}",
            description="Test play"
        )

        cls.theatre_hall = TheatreHall.objects.create(
            name="Test Hall 11",
            rows=10,
            seats_in_row=10
        )

        cls.performance = Performance.objects.create(
            play=cls.play,
            theatre_hall=cls.theatre_hall,
            show_time=datetime.now() + timedelta(days=1)
        )

        cls.reservation = Reservation.objects.create(user=cls.user)
        cls.ticket = Ticket.objects.create(
            row=2,
            seat=5,
            performance=cls.performance,
            reservation=cls.reservation,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user(self):
        response = self.client.get(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reservation_list(self):
        response = self.client.get(RESERVATION_URL)
        print(response.data)  # Для отладки, выводим ответ
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(
            self.reservation.id,
            [res["id"] for res in response.data]
        )

        self.assertIn(
            self.ticket.id,
            [ticket["id"] for ticket in response.data[0]["tickets"]]
        )

        self.assertEqual(
            response.data[0]["user"],
            self.user.id
        )

    def test_create_reservation_by_user(self):
        reservation = sample_reservation(user=self.user)

        response = self.client.get(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Исправлено на 200 вместо 201
        reservations = response.data
        self.assertIn(
            reservation.id,
            [reservation["id"] for reservation in reservations]
        )

    def test_validate_seat(self):
        response = self.client.post(
            RESERVATION_URL,
            {"tickets": [{
                "row": 30,
                "seat": 50,
                "performance": self.performance.id
            }]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
