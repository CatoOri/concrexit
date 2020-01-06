"""Defines the viewsets of the events package"""

from django.utils import timezone
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from events import services
from events.api.permissions import UnpublishedEventPermissions
from events.api.serializers import (
    EventCalenderJSSerializer,
    UnpublishedEventSerializer,
    EventRetrieveSerializer,
    EventListSerializer,
    RegistrationListSerializer,
    RegistrationAdminListSerializer,
    RegistrationSerializer,
)
from events.exceptions import RegistrationError
from events.models import Event, Registration
from utils.snippets import extract_date_range


class EventViewset(viewsets.ReadOnlyModelViewSet):
    """
    Defines the viewset for events, requires an authenticated user
    and enables ordering on the event start/end.
    """

    queryset = Event.objects.filter(published=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    ordering_fields = ("start", "end")
    search_fields = (
        "title_en",
        "title_nl",
    )

    def get_queryset(self):
        queryset = Event.objects.filter(published=True)

        if (
            self.action == "retrieve"
            or api_settings.SEARCH_PARAM in self.request.query_params
        ):
            return queryset

        start, end = extract_date_range(self.request, allow_empty=True)

        if start is not None:
            queryset = queryset.filter(start__gte=start)
        if end is not None:
            queryset = queryset.filter(end__lte=end)
        if start is None and end is None:
            queryset = queryset.filter(end__gte=timezone.now())

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        if self.action == "retrieve":
            return EventRetrieveSerializer
        return EventCalenderJSSerializer

    def get_serializer_context(self):
        return super().get_serializer_context()

    @action(detail=True, methods=["get", "post"], permission_classes=(IsAuthenticated,))
    def registrations(self, request, pk):
        """
        Defines a custom route for the event's registrations,
        can filter on registration status if the user is an organiser

        :param request: the request object
        :param pk: the primary key of the event
        :return: the registrations of the event
        """
        event = get_object_or_404(Event, pk=pk)

        if request.method.lower() == "post":
            try:
                registration = services.create_registration(request.member, event)
                serializer = RegistrationSerializer(
                    instance=registration, context={"request": request}
                )
                return Response(status=201, data=serializer.data)
            except RegistrationError as e:
                raise PermissionDenied(detail=e)

        status = request.query_params.get("status", None)

        # Make sure you can only access other registrations when you have
        # the permissions to do so
        if not services.is_organiser(request.member, event):
            status = "registered"

        queryset = Registration.objects.filter(event=pk)
        if status is not None:
            if status == "queued":
                queryset = Registration.objects.filter(event=pk, date_cancelled=None)[
                    event.max_participants :
                ]
            elif status == "cancelled":
                queryset = Registration.objects.filter(
                    event=pk, date_cancelled__not=None
                )
            elif status == "registered":
                queryset = Registration.objects.filter(event=pk, date_cancelled=None)[
                    : event.max_participants
                ]

        context = {"request": request}
        if services.is_organiser(self.request.member, event):
            serializer = RegistrationAdminListSerializer(
                queryset, many=True, context=context
            )
        else:
            serializer = RegistrationListSerializer(
                queryset, many=True, context=context
            )

        return Response(serializer.data)

    @action(detail=False, permission_classes=(IsAuthenticatedOrReadOnly,))
    def calendarjs(self, request):
        """
        Defines a custom route that outputs the correctly formatted
        events information for CalendarJS, published events only
        :param request: the request object

        :return: response containing the data
        """
        start, end = extract_date_range(request)

        queryset = Event.objects.filter(end__gte=start, start__lte=end, published=True)

        serializer = EventCalenderJSSerializer(
            queryset, many=True, context={"member": request.member}
        )
        return Response(serializer.data)

    @action(
        detail=False, permission_classes=(IsAdminUser, UnpublishedEventPermissions,)
    )
    def unpublished(self, request):
        """
        Defines a custom route that outputs the correctly formatted
        events information for CalendarJS, unpublished events only

        :param request: the request object
        :return: response containing the data
        """
        start, end = extract_date_range(request)

        queryset = Event.objects.filter(end__gte=start, start__lte=end, published=False)

        serializer = UnpublishedEventSerializer(
            queryset, many=True, context={"member": request.member}
        )
        return Response(serializer.data)


class RegistrationViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    Defines the viewset for registrations, requires an authenticated user.
    Has custom update and destroy methods that use the services.
    """

    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_object(self):
        instance = super().get_object()
        if (
            instance.name or instance.member.pk != self.request.member.pk
        ) and not services.is_organiser(self.request.member, instance.event):
            raise NotFound()

        return instance

    # Always set instance so that OPTIONS call will show the info fields too
    def get_serializer(self, *args, **kwargs):
        if len(args) == 0 and "instance" not in kwargs:
            kwargs["instance"] = self.get_object()
        return super().get_serializer(*args, **kwargs)

    def perform_update(self, serializer):
        registration = serializer.instance

        member = self.request.member
        if (
            member
            and member.has_perm("events.change_registration")
            and services.is_organiser(member, registration.event)
        ):
            services.update_registration_by_organiser(
                registration, self.request.member, serializer.validated_data
            )

        services.update_registration(
            registration=registration, field_values=serializer.field_values()
        )
        serializer.information_fields = services.registration_fields(
            serializer.context["request"], registration=registration
        )

    def destroy(self, request, pk=None, **kwargs):
        registration = self.get_object()
        try:
            services.cancel_registration(registration.member, registration.event)
            return Response(status=204)
        except RegistrationError as e:
            raise PermissionDenied(detail=e)
