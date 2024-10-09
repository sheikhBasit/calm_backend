from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from my_app.models import Profile, Appointment, Clinic, Professional, User


class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.professional = Professional.objects.create(
            user=self.user,
            specialization="Therapist",
            bio="Expert in therapy"
        )
        self.clinic = Clinic.objects.create(
            name="Main Clinic",
            address="123 Main St",
            phone="555-5555",
            email="clinic@example.com",
            latitude=10.0,
            longitude=20.0
        )
        self.appointment = Appointment.objects.create(
            user=self.user,
            professional=self.professional,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            status="Scheduled"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Bio of Test User",
            location="Test City",
            privacy_settings="Public"
        )

    def test_create_user_with_missing_email(self):
        url = reverse('user-list')
        data = {
            "name": "New User",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_user_with_invalid_email(self):
        url = reverse('user-list')
        data = {
            "name": "New User",
            "email": "not-an-email",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_fetch_non_existent_user(self):
        url = reverse('user-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_non_existent_health_data(self):
        url = reverse('healthdata-detail', kwargs={'pk': 999})
        data = {"mood": "Bad", "symptoms": "Headache"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_appointment_with_invalid_times(self):
        url = reverse('appointment-list')
        data = {
            "user": self.user.id,
            "professional": self.professional.id,
            "start_time": "2024-10-10T12:00:00Z",
            "end_time": "2024-10-10T11:00:00Z",  # Invalid, end time is before start time
            "status": "pending"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'End time must be after start time.')

    def test_fetch_feedback_for_non_existent_professional(self):
        non_existent_professional_id = 9999
        url = reverse('feedback-list') + f"?professional={non_existent_professional_id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_feedback_submission(self):
        url = reverse('feedback-list')
        data = {
            "message": ""  # Invalid: message should not be empty
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_create_feedback_with_valid_data(self):
        url = reverse('feedback-list')
        data = {
            "user": self.user.id,  # Ensure the user is included
            "message": "Great service!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

    def test_feedback_submission_with_invalid_user(self):
        other_user = User.objects.create_user(email="otheruser@example.com", name="Other User", password="password123")
        url = reverse('feedback-list')
        data = {
            "user": other_user.id,  # Invalid user (not the current authenticated user)
            "message": "Test feedback"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_professional_with_existing_email(self):
        # First, create a professional for the user
        Professional.objects.create(
            user=self.user,
            specialization="Therapist",
            bio="Bio of the first professional"
        )

        # Now attempt to create another professional with the same user
        url = reverse('professional-list')
        data = {
            "user": self.user.id,  # Use the existing user's ID
            "specialization": "Dentist",
            "bio": "Specialist in dental care"
        }

        response = self.client.post(url, data, format='json')

        # Assert that the response status code is 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)  # Ensure the error is related to the user
    def test_create_clinic_without_address(self):
        url = reverse('clinic-list')
        data = {
            "name": "New Clinic",
            "phone": "555-1234",
            "email": "newclinic@example.com",
            "latitude": 10.0,
            "longitude": 20.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('address', response.data)

    def test_fetch_user_profile(self):
        url = reverse('profile-detail', kwargs={'pk': self.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], self.profile.bio)

    def test_update_professional(self):
        url = reverse('professional-detail', args=[self.professional.id])
        data = {
            "specialization": "Updated Specialization",
            "bio": "Updated bio"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], "Updated Specialization")
