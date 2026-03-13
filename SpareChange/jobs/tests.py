from django.test import TestCase, Client
from django.urls import reverse
from .models import JobPost
from users.models import base_user
from datetime import date, timedelta
from .forms import JobPostForm

class JobModelTests(TestCase):
    """Tests for the JobPost model"""
    
    def setUp(self):
        """Create a test user and job before each test"""
        self.user = base_user.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.job = JobPost.objects.create(
            poster=self.user,
            title='Test Job',
            description='This is a test job description',
            location='Test City',
            pay=50.00,
            price_type='HR',
            estimated_hours=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
    
    def test_job_creation(self):
        """Test that a job can be created with all fields"""
        self.assertEqual(self.job.title, 'Test Job')
        self.assertEqual(self.job.poster.username, 'testuser')
        self.assertEqual(self.job.price_type, 'HR')
        self.assertEqual(self.job.get_price_type_display(), 'Hourly')
        self.assertFalse(self.job.hide_from_listings)
    
    def test_job_string_representation(self):
        """Test the string representation of the job"""
        # This will pass once you add __str__ to your model
        self.assertEqual(str(self.job), 'Test Job')
    
    def test_job_default_hidden_false(self):
        """Test that new jobs are not hidden by default"""
        self.assertFalse(self.job.hide_from_listings)
    
    def test_job_without_pay(self):
        """Test creating a job without pay (negotiable)"""
        job2 = JobPost.objects.create(
            poster=self.user,
            title='Negotiable Job',
            description='Pay negotiable',
            location='Test City',
            price_type='NG'
        )
        self.assertIsNone(job2.pay)
        self.assertEqual(job2.get_price_type_display(), 'Negotiable')


class JobViewTests(TestCase):
    """Tests for the job views"""
    
    def setUp(self):
        self.client = Client()
        self.user = base_user.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create a test job
        self.job = JobPost.objects.create(
            poster=self.user,
            title='Test Job',
            description='Test description',
            location='Test City',
            pay=50.00,
            price_type='HR'
        )
    
    def test_homepage_displays_jobs(self):
        """Test that jobs appear on the homepage"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')
        self.assertContains(response, 'Test City')
    
    def test_homepage_only_shows_active_jobs(self):
        """Test that hidden jobs don't appear on homepage"""
        # Create a hidden job
        hidden_job = JobPost.objects.create(
            poster=self.user,
            title='Hidden Job',
            description='Should not appear',
            location='Hidden City',
            hide_from_listings=True
        )
        
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Job')  # Visible job appears
        self.assertNotContains(response, 'Hidden Job')  # Hidden job doesn't appear
    
    def test_create_job_page_loads(self):
        """Test that create job page loads for logged in user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_job'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/create_job.html')
    
    def test_create_job_redirects_if_not_logged_in(self):
        """Test that non-logged in users can't access create job page"""
        response = self.client.get(reverse('create_job'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        # Fix: Use the correct login URL pattern
        self.assertRedirects(response, f'/accounts/login/?next={reverse("create_job")}')
    
    def test_create_job_post(self):
        """Test creating a new job via POST"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('create_job'), {
            'title': 'New Test Job',
            'description': 'New description',
            'location': 'New City',
            'pay': 75.00,
            'price_type': 'FL',
            'estimated_hours': 5,
        })
        
        # Check that job was created
        self.assertEqual(JobPost.objects.count(), 2)  # One from setUp + new one
        new_job = JobPost.objects.get(title='New Test Job')
        self.assertEqual(new_job.poster, self.user)
        self.assertEqual(new_job.price_type, 'FL')
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
    
    def test_create_job_without_pay(self):
        """Test creating a job with negotiable pay"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('create_job'), {
            'title': 'Negotiable Job',
            'description': 'Pay negotiable',
            'location': 'Test City',
            'price_type': 'NG',  # Negotiable
            # No pay field
        })
        
        new_job = JobPost.objects.get(title='Negotiable Job')
        self.assertIsNone(new_job.pay)
        self.assertEqual(new_job.price_type, 'NG')
    
    def test_create_job_with_invalid_data(self):
        """Test form validation with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('create_job'), {
            'title': '',  # Empty title should fail
            'description': 'Test',
            'location': 'Test',
            'price_type': 'FL',
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertContains(response, 'This field is required')


class JobOrderingTests(TestCase):
    """Test that jobs are ordered correctly"""
    
    def setUp(self):
        self.user = base_user.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create jobs with different dates
        from django.utils import timezone
        from datetime import timedelta
        
        self.old_job = JobPost.objects.create(
            poster=self.user,
            title='Old Job',
            description='Old',
            location='City',
            price_type='FL'
        )
        # Manually set created_at to 2 days ago
        self.old_job.created_at = timezone.now() - timedelta(days=2)
        self.old_job.save()
        
        self.new_job = JobPost.objects.create(
            poster=self.user,
            title='New Job',
            description='New',
            location='City',
            price_type='FL'
        )
        # created_at auto-set to now
    
    def test_jobs_ordered_by_created_at(self):
        """Test that jobs are ordered newest first"""
        jobs = JobPost.objects.filter(hide_from_listings=False).order_by('-created_at')
        self.assertEqual(jobs[0].title, 'New Job')  # Newest first
        self.assertEqual(jobs[1].title, 'Old Job')


# Form tests using your actual JobPostForm
class JobPostFormTests(TestCase):
    """Test the job creation form"""
    
    def test_valid_form_with_all_fields(self):
        """Test form is valid with all required fields"""
        form_data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'location': 'Test City',
            'pay': 100.00,
            'price_type': 'FL',
            'estimated_hours': 10,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=7),
            'is_recurring': False,
        }
        form = JobPostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_form_minimal_fields(self):
        """Test form is valid with only required fields"""
        form_data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'location': 'Test City',
            'price_type': 'FL',
        }
        form = JobPostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_missing_title(self):
        """Test form validation with missing title"""
        form_data = {
            'description': 'Test',
            'location': 'Test',
            'price_type': 'FL',
        }
        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_invalid_form_missing_price_type(self):
        """Test form validation with missing price_type"""
        form_data = {
            'title': 'Test Job',
            'description': 'Test',
            'location': 'Test',
        }
        form = JobPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price_type', form.errors)
    
    def test_form_excludes_correct_fields(self):
        """Test that the form excludes the right fields"""
        form = JobPostForm()
        self.assertNotIn('poster', form.fields)
        self.assertNotIn('created_at', form.fields)
        self.assertNotIn('updated_at', form.fields)
        self.assertNotIn('hide_from_listings', form.fields)
    
    def test_form_widgets(self):
        """Test that form uses correct widgets for date fields"""
        form = JobPostForm()
        self.assertEqual(form.fields['start_date'].widget.__class__.__name__, 'DateInput')
        self.assertEqual(form.fields['end_date'].widget.__class__.__name__, 'DateInput')
        self.assertIn('type="date"', str(form['start_date']))