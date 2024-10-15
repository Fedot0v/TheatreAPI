from datetime import datetime

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from theatre.models import Play, Genre, Actor, Reservation, TheatreHall, Performance
from theatre.serializers import (
    PlayDetailSerializer,
    PlaySerializer,
    PlayImageSerializer,
    GenreSerializer,
    GenreDetailSerializer,
    ActorSerializer,
    ActorDetailSerializer,
    ActorImageSerializer, PlayListSerializer, ReservationSerializer, TheatreHallSerializer, PerformanceSerializer
)
from theatre.utils import params_to_int


class ImageUploadMixin:
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading an image."""
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GenreDetailSerializer

        return GenreSerializer


class ActorViewSet(viewsets.ModelViewSet, ImageUploadMixin):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActorDetailSerializer

        if self.action == "upload_image":
            return ActorImageSerializer

        return ActorSerializer

    def get_queryset(self):
        """Retrieve the actors with filters"""
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset.distinct()


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_queryset(self):
        """Retrieve the plays with filters"""
        title = self.request.query_params.get("title")
        actors = self.request.query_params.get("actors")
        genres = self.request.query_params.get("genres")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if actors:
            actors_ids = params_to_int(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        if genres:
            genres_ids = params_to_int(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play",
        "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print(self.request.data)
        serializer.save(user=self.request.user)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset

        play = self.request.query_params.get("play")
        theatre_hall = self.request.query_params.get("theatre_hall")
        date = self.request.query_params.get("date")

        if play:
            play_ids = params_to_int(play)
            queryset = queryset.filter(play_id__in=play_ids)

        if theatre_hall:
            theatre_hall_ids = params_to_int(theatre_hall)
            queryset = queryset.filter(theatre_hall_id__in=theatre_hall_ids)

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        return queryset