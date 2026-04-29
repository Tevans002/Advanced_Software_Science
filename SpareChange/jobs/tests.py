import unittest
from django.test import TestCase, Client
from django.urls import reverse
from .models import JobPost
from users.models import base_user
from datetime import date, timedelta
from .forms import JobPostForm
from django.core.exceptions import ValidationError
import json
from unittest.mock import patch

# patch geocoding for all tests in this file
geocode_patch = patch(
    "location.models.Location._geocode", return_value=(46.8721, -113.9940)
)
geocode_patch.start()


class JobModelTests(TestCase):
    """Tests for the JobPost model"""

    def setUp(self):
        """Create a test user and job before each test"""
        self.user = base_user.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        self.job = JobPost.objects.create(
            poster=self.user,
            title="Test Job",
            description="This is a test job description",
            location="Test City",
            pay=50.00,
            price_type="HR",
            estimated_hours=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

    def test_job_creation(self):
        """Test that a job can be created with all fields"""
        self.assertEqual(self.job.title, "Test Job")
        self.assertEqual(self.job.poster.username, "testuser")
        self.assertEqual(self.job.price_type, "HR")
        self.assertEqual(self.job.get_price_type_display(), "Hourly")
        self.assertFalse(self.job.hide_from_listings)

    def test_job_string_representation(self):
        """Test the string representation of the job"""
        self.assertEqual(str(self.job), "Test Job")

    def test_job_default_hidden_false(self):
        """Test that new jobs are not hidden by default"""
        self.assertFalse(self.job.hide_from_listings)

    def test_job_without_pay(self):
        """Test creating a job without pay (negotiable)"""
        job2 = JobPost.objects.create(
            poster=self.user,
            title="Negotiable Job",
            description="Pay negotiable",
            location="Test City",
            price_type="NG",
            start_date=date.today(),  # Add start date
        )
        self.assertIsNone(job2.pay)
        self.assertEqual(job2.get_price_type_display(), "Negotiable")


class JobViewTests(TestCase):
    """Tests for the job views"""

    def setUp(self):
        self.client = Client()
        self.user = base_user.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create a test job
        self.job = JobPost.objects.create(
            poster=self.user,
            title="Test Job",
            description="Test description",
            location="Test City",
            pay=50.00,
            price_type="HR",
            start_date=date.today(),  # Add start date
        )

    def test_homepage_displays_jobs(self):
        """Test that jobs appear on the homepage"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Job")
        self.assertContains(response, "Test City")

    def test_homepage_only_shows_active_jobs(self):
        """Test that hidden jobs don't appear on homepage"""
        # Create a hidden job
        hidden_job = JobPost.objects.create(
            poster=self.user,
            title="Hidden Job",
            description="Should not appear",
            location="Hidden City",
            hide_from_listings=True,
            start_date=date.today(),  # Add start date
        )

        response = self.client.get(reverse("home"))
        self.assertContains(response, "Test Job")  # Visible job appears
        self.assertNotContains(response, "Hidden Job")  # Hidden job doesn't appear

    def test_create_job_page_loads(self):
        """Test that create job page loads for logged in user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("create_job"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/create_job.html")

    def test_create_job_redirects_if_not_logged_in(self):
        """Test that non-logged in users can't access create job page"""
        response = self.client.get(reverse("create_job"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, f'/accounts/login/?next={reverse("create_job")}')

    def test_create_job_post(self):
        """Test creating a new job via POST"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("create_job"),
            {
                "title": "New Test Job",
                "description": "New description",
                "location": "New City",
                "pay": 75.00,
                "price_type": "FL",
                "estimated_hours": 5,
                "start_date": date.today().isoformat(),  # Add start date
            },
        )

        # Check that job was created
        self.assertEqual(JobPost.objects.count(), 2)  # One from setUp + new one
        new_job = JobPost.objects.get(title="New Test Job")
        self.assertEqual(new_job.poster, self.user)
        self.assertEqual(new_job.price_type, "FL")

        # Check redirect
        self.assertEqual(response.status_code, 302)

    def test_create_job_without_pay(self):
        """Test creating a job with negotiable pay"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("create_job"),
            {
                "title": "Negotiable Job",
                "description": "Pay negotiable",
                "location": "Test City",
                "price_type": "NG",  # Negotiable
                "start_date": date.today().isoformat(),  # Add start date
                # No pay field
            },
        )

        new_job = JobPost.objects.get(title="Negotiable Job")
        self.assertIsNone(new_job.pay)
        self.assertEqual(new_job.price_type, "NG")

    def test_create_job_with_invalid_data(self):
        """Test form validation with invalid data"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("create_job"),
            {
                "title": "",  # Empty title should fail
                "description": "Test",
                "location": "Test",
                "price_type": "FL",
                "start_date": date.today().isoformat(),  # Add start date
            },
        )

        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertContains(response, "This field is required")


class JobOrderingTests(TestCase):
    """Test that jobs are ordered correctly"""

    def setUp(self):
        self.user = base_user.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Create jobs with different dates
        from django.utils import timezone
        from datetime import timedelta

        self.old_job = JobPost.objects.create(
            poster=self.user,
            title="Old Job",
            description="Old",
            location="City",
            price_type="FL",
            start_date=date.today(),  # Add start date
        )
        # Manually set created_at to 2 days ago
        self.old_job.created_at = timezone.now() - timedelta(days=2)
        self.old_job.save()

        self.new_job = JobPost.objects.create(
            poster=self.user,
            title="New Job",
            description="New",
            location="City",
            price_type="FL",
            start_date=date.today(),  # Add start date
        )
        # created_at auto-set to now

    def test_jobs_ordered_by_created_at(self):
        """Test that jobs are ordered newest first"""
        jobs = JobPost.objects.filter(hide_from_listings=False).order_by("-created_at")
        self.assertEqual(jobs[0].title, "New Job")  # Newest first
        self.assertEqual(jobs[1].title, "Old Job")


# Form tests for actual JobPostForm
class JobPostFormTests(TestCase):
    """Test the job creation form"""

    def test_valid_form_with_all_fields(self):
        """Test form is valid with all required fields"""
        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Test City",
            "pay": 100.00,
            "price_type": "FL",
            "estimated_hours": 10,
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=7)).isoformat(),
            "is_recurring": False,
        }
        form = JobPostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_form_minimal_fields(self):
        """Test form is valid with only required fields"""
        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Test City",
            "price_type": "FL",
            "pay": 50.00,
            "start_date": date.today().isoformat(),  # Add start date
        }
        form = JobPostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        """Test form validation with missing title"""
        form_data = {
            "description": "Test",
            "location": "Test",
            "price_type": "FL",
            "start_date": date.today().isoformat(),  # Add start date
        }
        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_invalid_form_missing_price_type(self):
        """Test form validation with missing price_type"""
        form_data = {
            "title": "Test Job",
            "description": "Test",
            "location": "Test",
            "start_date": date.today().isoformat(),  # Add start date
        }
        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("price_type", form.errors)

    def test_pay_too_high(self):
        """Test that pay over 999,999.99 is rejected"""
        form_data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'location': 'Test City',
            'price_type': 'FL',
            'pay': 1000000.00,
            'start_date': date.today(),
        }
        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pay', form.errors)

    def test_form_excludes_correct_fields(self):
        """Test that the form excludes the right fields"""
        form = JobPostForm()
        self.assertNotIn("poster", form.fields)
        self.assertNotIn("created_at", form.fields)
        self.assertNotIn("updated_at", form.fields)
        self.assertNotIn("hide_from_listings", form.fields)

    def test_form_widgets(self):
        """Test that form uses correct widgets for date fields"""
        form = JobPostForm()
        self.assertEqual(
            form.fields["start_date"].widget.__class__.__name__, "DateInput"
        )
        self.assertEqual(form.fields["end_date"].widget.__class__.__name__, "DateInput")
        self.assertIn('type="date"', str(form["start_date"]))

        # ========== NEW LOCATION VALIDATION TESTS ==========
    
    def test_valid_location_passes_validation(self):
        """Test that a valid geocodable address passes validation"""
        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Missoula, MT",  # Valid address
            "price_type": "FL",
            "pay": 50.00,
            "start_date": date.today().isoformat(),
        }
        form = JobPostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_location_fails_validation(self):
        """Test that an invalid geocodable address fails validation"""
        # Temporarily patch _geocode to raise ValueError for this test only
        with patch("location.models.Location._geocode") as mock_geocode:
            mock_geocode.side_effect = ValueError("Could not geocode: invalid")
            
            form_data = {
                "title": "Test Job",
                "description": "Test Description",
                "location": "invalid address that fails",
                "price_type": "FL",
                "pay": 50.00,
                "start_date": date.today().isoformat(),
            }
            form = JobPostForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("location", form.errors)
    
    def test_empty_location_fails_validation(self):
        """Test that empty location fails validation"""
        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "",  # Empty
            "price_type": "FL",
            "pay": 50.00,
            "start_date": date.today().isoformat(),
        }
        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("location", form.errors)
    
    def test_location_geocode_api_error_handled(self):
        """Test that API errors are caught and shown to user"""
        with patch("location.models.Location._geocode") as mock_geocode:
            # Simulate a network/API error
            mock_geocode.side_effect = Exception("API connection failed")
            
            form_data = {
                "title": "Test Job",
                "description": "Test Description",
                "location": "Some Address",
                "price_type": "FL",
                "pay": 50.00,
                "start_date": date.today().isoformat(),
            }
            form = JobPostForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("location", form.errors)

# ADDED TESTS FOR NEGATIVE PAY VALIDATION
class JobModelValidationTests(TestCase):
    """Test model validations"""

    def setUp(self):
        self.user = base_user.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_pay_cannot_be_negative(self):
        """Test that negative pay raises validation error"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            pay=-50.00,  # Negative pay
            price_type="FL",
            start_date=date.today(),  # Add start date
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_pay_cannot_be_zero(self):
        """Test that zero pay raises validation error"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            pay=0.00,  # Zero pay
            price_type="FL",
            start_date=date.today(),  # Add start date
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_pay_required_for_flat_rate(self):
        """Test that pay is required for flat rate jobs"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            pay=None,  # No pay
            price_type="FL",  # Flat rate requires pay
            start_date=date.today(),  # Add start date
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_pay_optional_for_negotiable(self):
        """Test that pay can be null for negotiable jobs"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            pay=None,
            price_type="NG",  # Negotiable
            start_date=date.today(),  # Add start date
        )

        try:
            job.full_clean()
        except ValidationError:
            self.fail("Negotiable job with null pay raised validation error")

    def test_positive_pay_valid(self):
        """Test that positive pay is valid"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            pay=50.00,  # Positive pay
            price_type="FL",
            start_date=date.today(),  # Add start date
        )

        try:
            job.full_clean()
        except ValidationError:
            self.fail("Valid job with positive pay raised validation error")

    # ========== NEW LOCATION MODEL VALIDATION TESTS ==========
    
    def test_invalid_location_raises_validation_error_at_model_level(self):
        """Test that invalid location raises ValidationError in model.clean()"""
        with patch("location.models.Location._geocode") as mock_geocode:
            mock_geocode.side_effect = ValueError("Could not geocode")
            
            job = JobPost(
                poster=self.user,
                title="Test Job",
                description="Test Description",
                location="invalid address",
                price_type="FL",
                pay=50.00,
                start_date=date.today(),
            )
            
            with self.assertRaises(ValidationError):
                job.full_clean()
    
    def test_valid_location_passes_model_validation(self):
        """Test that valid location passes model validation"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Missoula, MT",  # Will use the global patch
            price_type="FL",
            pay=50.00,
            start_date=date.today(),
        )
        
        try:
            job.full_clean()
        except ValidationError:
            self.fail("Valid job with good location raised validation error")

# ADDED TESTS FOR DATE VALIDATION
class JobDateValidationTests(TestCase):
    """Test date validations for jobs"""

    def setUp(self):
        self.user = base_user.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_start_date_required(self):
        """Test that start date is required"""
        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=None,  # No start date
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_start_date_cannot_be_in_past(self):
        """Test that start date in the past raises validation error"""
        past_date = date.today() - timedelta(days=1)

        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=past_date,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_end_date_cannot_be_in_past(self):
        """Test that end date in the past raises validation error"""
        past_date = date.today() - timedelta(days=1)

        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=date.today(),
            end_date=past_date,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_start_date_can_be_today(self):
        """Test that start date can be today"""
        today = date.today()

        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=today,
        )

        try:
            job.full_clean()
        except ValidationError:
            self.fail("Start date of today raised validation error")

    def test_start_date_can_be_future(self):
        """Test that start date can be in the future"""
        future_date = date.today() + timedelta(days=7)

        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=future_date,
        )

        try:
            job.full_clean()
        except ValidationError:
            self.fail("Future start date raised validation error")

    def test_end_date_after_start_date(self):
        """Test that end date must be after start date"""
        start_date = date.today() + timedelta(days=7)
        end_date = date.today() + timedelta(days=1)

        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=start_date,
            end_date=end_date,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_end_date_after_start_date_valid(self):
        """Test that end date after start date is valid"""
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=7)

        job = JobPost(
            poster=self.user,
            title="Test Job",
            description="Test Description",
            location="Test City",
            price_type="FL",
            pay=50.00,
            start_date=start_date,
            end_date=end_date,
        )

        try:
            job.full_clean()
        except ValidationError:
            self.fail("Valid date range raised validation error")

    def test_form_start_date_required(self):
        """Test that form shows error when start date is missing"""
        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Test City",
            "price_type": "FL",
            "pay": 50.00,
        }

        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)

    def test_form_start_date_past_error(self):
        """Test that form shows error for past start date"""
        past_date = date.today() - timedelta(days=1)

        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Test City",
            "price_type": "FL",
            "pay": 50.00,
            "start_date": past_date.isoformat(),
        }

        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)

    def test_form_end_date_past_error(self):
        """Test that form shows error for past end date"""
        past_date = date.today() - timedelta(days=1)

        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Test City",
            "price_type": "FL",
            "pay": 50.00,
            "start_date": date.today().isoformat(),
            "end_date": past_date.isoformat(),
        }

        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_form_dates_valid(self):
        """Test that valid dates pass form validation"""
        start_date = date.today()
        end_date = date.today() + timedelta(days=14)

        form_data = {
            "title": "Test Job",
            "description": "Test Description",
            "location": "Test City",
            "price_type": "FL",
            "pay": 50.00,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        form = JobPostForm(data=form_data)
        self.assertTrue(form.is_valid())

# TEST CLASS FOR AI ENHANCEMENT USING LLM
try:
    from ollama import Client as OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

@unittest.skipIf(not OLLAMA_AVAILABLE, "Ollama not installed")
class AIEnhancementTests(TestCase):
    """Tests for the AI job description enhancement feature"""
    
    def setUp(self):
        """Set up test client and URL"""
        # django client not ollama
        self.client = Client()
        self.enhance_url = reverse('enhance_description')
        self.user = base_user.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    @patch('jobs.views.ollama_client')
    def test_enhance_endpoint_returns_success(self, mock_ollama):
        """Test that enhance endpoint returns enhanced description"""
        # Mock Ollama response
        mock_response = {
            'message': {
                'content': 'This is an enhanced professional job description.'
            }
        }
        mock_ollama.chat.return_value = mock_response
        
        # Make request
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({'description': 'basic job description'}),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('enhanced_description', data)
        self.assertEqual(data['enhanced_description'], 'This is an enhanced professional job description.')
    
    def test_enhance_endpoint_handles_empty_description(self):
        """Test that empty description returns error"""
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({'description': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_enhance_endpoint_handles_missing_description(self):
        """Test that missing description field returns error"""
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('jobs.views.ollama_client')
    def test_enhance_endpoint_handles_ollama_exception(self, mock_ollama):
        """Test that Ollama exception is handled gracefully"""
        # Mock an exception
        mock_ollama.chat.side_effect = Exception("Ollama connection error")
        
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({'description': 'test description'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('jobs.views.ollama_client')
    def test_enhance_endpoint_handles_very_long_description(self, mock_ollama):
        """Test that very long descriptions are handled"""
        # Mock successful Ollama response
        mock_response = {
            'message': {
                'content': 'Enhanced long description'
            }
        }
        mock_ollama.chat.return_value = mock_response
        
        # Create a very long description (2000 characters)
        long_description = "a " * 1000
        
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({'description': long_description}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_enhance_endpoint_requires_post_method(self):
        """Test that GET requests are not allowed"""
        response = self.client.get(self.enhance_url)
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_enhance_endpoint_handles_malformed_json(self):
        """Test that malformed JSON returns error"""
        response = self.client.post(
            self.enhance_url,
            data='not valid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('jobs.views.ollama_client')
    def test_enhance_endpoint_passes_correct_parameters(self, mock_ollama):
        """Test that the correct parameters are passed to Ollama"""
        mock_response = {
            'message': {
                'content': 'Enhanced text'
            }
        }
        mock_ollama.chat.return_value = mock_response
        
        original_description = "Need a plumber for leaky faucet"
        
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({'description': original_description}),
            content_type='application/json'
        )

        # Verify HTTP response is correct
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['enhanced_description'], 'Enhanced text')
        
        # Verify Ollama was called once
        self.assertEqual(mock_ollama.chat.call_count, 1)
        
        # Get the arguments passed to ollama_client.chat
        call_args = mock_ollama.chat.call_args[1]
        
        # Verify the correct model was used
        self.assertEqual(call_args.get('model'), 'llama3.2:1b')
        
        # Verify the prompt contains the original description
        messages = call_args.get('messages', [])
        self.assertTrue(len(messages) > 0)
        self.assertIn(original_description, messages[0].get('content', ''))
    
    @patch('jobs.views.ollama_client')
    def test_enhance_endpoint_strips_prompt_artifacts(self, mock_ollama):
        """Test that the endpoint removes 'Improved description:' prefix if present"""
        # Mock response that includes the prefix
        mock_response = {
            'message': {
                'content': 'Improved description: This is the actual enhanced text.'
            }
        }
        mock_ollama.chat.return_value = mock_response
        
        response = self.client.post(
            self.enhance_url,
            data=json.dumps({'description': 'test description'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # The prefix should be stripped
        self.assertEqual(data['enhanced_description'], 'This is the actual enhanced text.')