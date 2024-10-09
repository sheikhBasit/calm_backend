from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'healthdata', views.HealthDataViewSet)
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')
router.register(r'professionals', views.ProfessionalViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'clinics', views.ClinicViewSet)

urlpatterns = [
    path('', include(router.urls)),
]