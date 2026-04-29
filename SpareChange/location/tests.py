from django.test import TestCase
from location.models import Location
from unittest.mock import patch

# Create your tests here.
class LocationModelTests(TestCase):
    """Tests for the Location model geocoding"""
    
    def test_geocode_valid_address_returns_coordinates(self):
        """Test that _geocode returns coordinates for valid address"""
        with patch("location.models.requests.get") as mock_get:
            # Mock the API response
            mock_response = mock_get.return_value
            mock_response.json.return_value = [
                {"lat": "46.8721", "lon": "-113.9940"}
            ]
            
            lat, lng = Location._geocode("Missoula, MT")
            
            self.assertEqual(lat, 46.8721)
            self.assertEqual(lng, -113.9940)
    
    def test_geocode_invalid_address_raises_value_error(self):
        """Test that _geocode raises ValueError for invalid address"""
        with patch("location.models.requests.get") as mock_get:
            # Mock empty response (no results)
            mock_response = mock_get.return_value
            mock_response.json.return_value = []
            
            with self.assertRaises(ValueError) as context:
                Location._geocode("invalid address")
            
            self.assertIn("Could not geocode", str(context.exception))
    
    def test_geocode_api_error_raises_exception(self):
        """Test that API errors are propagated"""
        with patch("location.models.requests.get") as mock_get:
            # Mock a request exception
            mock_get.side_effect = Exception("Network error")
            
            with self.assertRaises(Exception):
                Location._geocode("Some Address")
    
    def test_create_for_job_creates_location_with_fuzzed_coords(self):
        """Test that create_for_job creates a location with fuzzed coordinates"""
        with patch("location.models.Location._geocode") as mock_geocode:
            mock_geocode.return_value = (46.8721, -113.9940)
            
            with patch("location.models.Location._fuzz") as mock_fuzz:
                mock_fuzz.return_value = (46.9000, -114.0000)
                
                location = Location.create_for_job("Missoula, MT")
                
                self.assertEqual(location.location_type, "job")
                self.assertEqual(location.raw_input, "Missoula, MT")
                self.assertEqual(location.lat, 46.8721)
                self.assertEqual(location.lng, -113.9940)
                self.assertEqual(location.fuzzed_lat, 46.9000)
                self.assertEqual(location.fuzzed_lng, -114.0000)
    
    def test_create_for_user_creates_location_without_fuzzing(self):
        """Test that create_for_user creates a location without fuzzing"""
        with patch("location.models.Location._geocode") as mock_geocode:
            mock_geocode.return_value = (46.8721, -113.9940)
            
            location = Location.create_for_user("Missoula, MT")
            
            self.assertEqual(location.location_type, "user")
            self.assertEqual(location.raw_input, "Missoula, MT")
            self.assertEqual(location.lat, 46.8721)
            self.assertEqual(location.lng, -113.9940)
            self.assertIsNone(location.fuzzed_lat)
            self.assertIsNone(location.fuzzed_lng)