from django.http import Http404
from rest_framework import viewsets, filters, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Profile, Assessment, HealthData, Feedback, Professional, Appointment, Clinic
from .serializers import (UserSerializer, ProfileSerializer, AssessmentSerializer, HealthDataSerializer,
                          FeedbackSerializer, ProfessionalSerializer, AppointmentSerializer, ClinicSerializer)
from .permissions import IsOwner, IsProfessionalOrReadOnly
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'email']
    search_fields = ['name', 'email']
    ordering_fields = ['id', 'name', 'email']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance:
            return Response({'error': 'You are not allowed to delete this account.'}, status=403)
        return super().destroy(request, *args, **kwargs)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['user__name', 'location']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.user:
            return Response({'error': 'You can only update your own profile.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.user:
            return Response({'error': 'You are not allowed to delete this profile.'}, status=403)
        return super().destroy(request, *args, **kwargs)


class AssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['type']


class HealthDataViewSet(viewsets.ModelViewSet):
    queryset = HealthData.objects.all()
    serializer_class = HealthDataSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]  # Allow GET, HEAD, OPTIONS
        return [permissions.IsAuthenticated()]  # Require authentication for other methods


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    queryset = Feedback.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Associate the feedback with the authenticated user

    def create(self, request, *args, **kwargs):
        # Ensure the user in the request matches the authenticated user
        user_id = request.data.get("user")
        if user_id and int(user_id) != request.user.id:
            return Response({'error': 'You are not allowed to submit feedback as another user.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        professional_id = self.request.query_params.get('professional', None)
        if professional_id is not None:
            if not Professional.objects.filter(id=professional_id).exists():
                raise Http404("Professional not found")  # This will return a 404 error
            return queryset.filter(user__professional__id=professional_id)
        return queryset


class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['user__name', 'specialization']

    def list(self, request, *args, **kwargs):
        professionals = Professional.objects.all()
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        if start_time and end_time:
            appointments = Appointment.objects.filter(professional__in=professionals, start_time=start_time,
                                                      end_time=end_time)
            return Response({'professionals': professionals, 'appointments': appointments})
        return super().list(request, *args, **kwargs)

    # You might not need to override perform_create
    # def perform_create(self, serializer):
    #     serializer.save()


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'professional', 'status']
    search_fields = ['professional__user__name', 'status']


class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['latitude', 'longitude', 'email', 'name']
    search_fields = ['name', 'email']
