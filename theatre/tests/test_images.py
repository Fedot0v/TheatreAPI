import os
import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from theatre.tests.test_utils import sample_play, sample_actor


@pytest.mark.django_db
class ImageUploadTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_actor_and_play_image_upload(self):
        image_file = SimpleUploadedFile(
            name=f'test_image_{uuid.uuid4()}.jpg',
            content=b'file_content',
            content_type='image/jpeg'
        )

        actor = sample_actor(image=image_file)

        play = sample_play(image=image_file)

        self.assertTrue(actor.image.name.startswith('uploads/images/'))
        self.assertTrue(actor.image.name.endswith('.jpg'))

        self.assertTrue(os.path.exists(actor.image.path))

        os.remove(actor.image.path)
        os.remove(play.image.path)
