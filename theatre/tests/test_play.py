import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from theatre.models import Play
from theatre.serializers import PlayListSerializer, PlayDetailSerializer
from theatre.tests.test_utils import sample_play, sample_actor, sample_genre

PLAY_URL = reverse("theatre:play-list")

def detail_url(performance_id):
    return reverse("theatre:play-detail", args=[performance_id])


@pytest.mark.django_db
class UnauthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PLAY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class AuthenticatedUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email=f"testuser-{uuid.uuid4()}@test.com",
            password="testpassword",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_plays_list(self):
        actor = sample_actor()
        genre = sample_genre()
        play = sample_play()
        play.genres.add(genre)
        play.actors.add(actor)

        response = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_plays_by_genre(self):
        genre1 = sample_genre(name="Drama")
        genre2 = sample_genre(name="Comedy")
        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")
        play1.genres.add(genre1)
        play2.genres.add(genre2)

        response = self.client.get(
            PLAY_URL,
            {"genres": f"{genre1.id},{genre2.id}"}
        )

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_filter_plays_by_actor(self):
        actor1 = sample_actor(first_name="test", last_name="test")
        actor2 = sample_actor(first_name="test1", last_name="test1")

        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        play1.actors.add(actor1, actor2)
        play2.actors.add(actor2)

        response = self.client.get(PLAY_URL, {"actors": actor2.id})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.genres.add(sample_genre())
        play.actors.add(sample_actor())

        url = detail_url(play.id)

        response = self.client.get(url)

        serializer = PlayDetailSerializer(play)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_cannot_create_play(self):
        payload = {
            "title": "Test play",
            "description": "Test play",
        }

        response = self.client.post(PLAY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class AdminPlayTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="testadmin@test.com",
            password="testpassword",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_play(self):
        payload = {
            "title": f"Test play {uuid.uuid4()}",
            "description": "Test play",
        }

        response = self.client.post(PLAY_URL, payload)

        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=response.data["id"])

        for key in payload:
            self.assertEqual(payload[key], getattr(play, key))

    def test_invalid_play(self):
        payload = {
            "title": "",
            "description": "Test play",
        }

        response = self.client.post(PLAY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_play_with_actors(self):
        actor1 = sample_actor(first_name="test", last_name="test")
        actor2 = sample_actor(first_name="test1", last_name="test1")
        payload = {
            "title": f"Test play {uuid.uuid4()}",
            "description": "Test play",
            "actors": [actor1.id, actor2.id],
        }

        response = self.client.post(PLAY_URL, payload)

        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=response.data["id"])
        actors = play.actors.all()

        self.assertIn(actor1, actors)
        self.assertIn(actor2, actors)
        self.assertEqual(actors.count(), 2)

    def test_create_play_with_genres(self):
        genre1 = sample_genre(name="Drama")
        genre2 = sample_genre(name="Comedy")

        payload = {
            "title": f"Test play {uuid.uuid4()}",
            "description": "Test play",
            "genres": [genre1.id, genre2.id],
        }

        response = self.client.post(PLAY_URL, payload)

        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=response.data["id"])
        genres = play.genres.all()

        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)
        self.assertEqual(genres.count(), 2)
