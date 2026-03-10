from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LoginSystemTest(TestCase):

    def setUp(self):
        self.username = "mytestuser"
        self.password = "passwordset12345"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        print("User created: ", self.user)

    def testHomePageAnon(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not logged in.")
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('signup'))
        print("Home page loaded")

    def testLoginPageLoads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        print("Login page loaded")

    def testLoginSuccessful(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        }, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, f"Hello, <strong>{self.username}</strong>!")
        self.assertTrue(response.context['user'].is_authenticated)
        print("Login successful")

    def testLoginInvalidPassword(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword'
        })  
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        print("Login invalid password")

    def testLogout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('login'))
        print("Logout successful")

    def testSignupPageLoads(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        print("Signup page loaded")
        
    def testSignupSuccessful(self):
        new_username = "newuser"
        new_password = "newpassword123"
        response = self.client.post(reverse('signup'), {
            'username': new_username,
            'password1': new_password,
            'password2': new_password,
        }, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username=new_username).exists())
        print("Signup successful")