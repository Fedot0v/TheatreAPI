import datetime

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Performance
from theatre.serializers import (
    PerformanceListSerializer,
    PerformanceDetailSerializer,
)
from theatre.tests.test_utils import (
    sample_play,
    sample_performance,
    sample_theatre_hall,
)

PERFORMANCE_URL = reverse("theatre:performance-list")


def detail_url(performance_id):
    return reverse("theatre:performance-detail", args=[performance_id])


class TestUnauthenticatedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class TestAuthenticatedUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password123",
        )
        cls.theatre_hall = sample_theatre_hall()
        cls.play = sample_play()
        cls.performance = sample_performance(
            play=cls.play,
            theatre_hall=cls.theatre_hall,
            show_time=datetime.datetime(2024, 11, 10, 18, 30)
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_auth_required(self):
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_available_seats_count(self):
        expected_count = len(self.performance.get_free_seats())
        serializer = PerformanceListSerializer(self.performance)
        self.assertEqual(serializer.data["available_seats_count"], expected_count)

    def test_performance_list(self):
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.performance.id, [performance['id'] for performance in response.data])

    def test_performance_detail(self):
        response = self.client.get(detail_url(self.performance.id))
        serializer = PerformanceDetailSerializer(self.performance)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_filter_performance_by_play(self):
        response = self.client.get(PERFORMANCE_URL, {"play": self.play.id})
        serializer = PerformanceListSerializer(self.performance)
        self.assertIn(serializer.data, response.data)

    def test_filter_performance_by_hall(self):
        response = self.client.get(PERFORMANCE_URL, {"theatre_hall": self.theatre_hall.id})
        serializer = PerformanceListSerializer(self.performance)
        self.assertIn(serializer.data, response.data)

    def test_filter_performance_by_date(self):
        show_time_date = self.performance.show_time.date()
        response = self.client.get(PERFORMANCE_URL, {"date": show_time_date.isoformat()})
        serializer = PerformanceListSerializer(self.performance)
        self.assertIn(serializer.data, response.data)

    def test_user_cannot_create_performance(self):
        payload = {
            "play": self.play.id,
            "theatre_hall": self.theatre_hall.id,
            "show_time": "2024-11-10T18:30:00"
        }
        response = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestAdminUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="super@mail.com",
            password="password123",
        )
        cls.theatre_hall = sample_theatre_hall()
        cls.play = sample_play()
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_performance(self):
        payload = {
            "play": self.play.id,
            "theatre_hall": self.theatre_hall.id,
            "show_time": "2024-11-10T18:30:00"
        }
        response = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        performance = Performance.objects.get(id=response.data["id"])
        self.assertEqual(performance.play.id, payload["play"])
        self.assertEqual(performance.theatre_hall.id, payload["theatre_hall"])
        self.assertEqual(performance.show_time.strftime('%Y-%m-%dT%H:%M:%S'), payload["show_time"])

    def test_invalid_performance(self):
        payload = {
            "theatre_hall": self.theatre_hall.id,
            "show_time": "2024-11-10T18:30:00"
        }
        response = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
