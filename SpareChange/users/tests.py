from django.test import TestCase
from django.urls import reverse

# from django.contrib.auth.models import User
from users.models import base_user


class LoginSystemTest(TestCase):

    def setUp(self):
        self.username = "mytestuser"
        self.password = "passwordset12345"
        self.user = base_user.objects.create_user(
            username=self.username, password=self.password
        )
        print("User created: ", self.user)

    def testHomePageAnon(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not logged in.")
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("signup"))
        print("Home page loaded")

    def testLoginPageLoads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        print("Login page loaded")

    def testLoginSuccessful(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
            follow=True,
        )
        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, f"Hello, <strong>{self.username}</strong>!")
        self.assertTrue(response.context["user"].is_authenticated)
        print("Login successful")

    def testLoginInvalidPassword(self):
        response = self.client.post(
            reverse("login"), {"username": self.username, "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        print("Login invalid password")

    def testLogout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse("logout"), follow=True)
        self.assertRedirects(response, reverse("login"))
        print("Logout successful")

    def testSignupPageLoads(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")
        print("Signup page loaded")

    def testSignupSuccessful(self):
        new_username = "newuser"
        new_password = "newpassword123"
        response = self.client.post(
            reverse("signup"),
            {
                "username": new_username,
                "password1": new_password,
                "password2": new_password,
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(base_user.objects.filter(username=new_username).exists())
        print("Signup successful")

    # added to check additional fields added to model/schema
    def testSignupFields(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "fieldtestuser",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
                "user_bio": "This is my bio.",
                "zipcode": "59801",
                "date_of_birth": "1990-01-01",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("login"))

        user = base_user.objects.get(username="fieldtestuser")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john@example.com")
        self.assertEqual(user.user_bio, "This is my bio.")
        self.assertEqual(user.zipcode, "59801")
        self.assertEqual(str(user.date_of_birth), "1990-01-01")
        self.assertFalse(user.is_verified)
        print("Signup fields test passed")
