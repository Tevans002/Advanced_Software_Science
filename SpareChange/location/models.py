import random
import math
import requests
from django.db import models

NOMINATIM_USER_AGENT = "SpareChange/1.0"


class Location(models.Model):
    LOCATION_TYPE_CHOICES = [("user", "User"), ("job", "Job")]

    location_type = models.CharField(max_length=4, choices=LOCATION_TYPE_CHOICES)
    raw_input = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fuzzed_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    fuzzed_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    search_radius_miles = models.PositiveIntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location_type} | {self.raw_input}"

    # class methods called from other models overwritten save() method

    @classmethod
    def create_for_user(cls, raw_input):
        lat, lng = cls._geocode(raw_input)
        return cls.objects.create(
            location_type="user",
            raw_input=raw_input,
            lat=lat,
            lng=lng,
        )

    @classmethod
    def create_for_job(cls, raw_input, coords=None):
        lat, lng = coords if coords else cls._geocode(raw_input)
        fuzzed_lat, fuzzed_lng = cls._fuzz(lat, lng)
        return cls.objects.create(
            location_type="job",
            raw_input=raw_input,
            lat=lat,
            lng=lng,
            fuzzed_lat=fuzzed_lat,
            fuzzed_lng=fuzzed_lng,
        )

    # methods for updating location object itself

    def update_from_zip(self, zipcode):
        self.raw_input = zipcode
        self.lat, self.lng = self._geocode(zipcode)
        self.save()

    def update_from_coords(self, lat, lng):
        self.lat = lat
        self.lng = lng
        self.raw_input = self._reverse_geocode(lat, lng) or self.raw_input
        self.save()

    # helpers

    @staticmethod
    def _geocode(raw_input):
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": raw_input, "format": "json", "limit": 1},
            headers={"User-Agent": NOMINATIM_USER_AGENT},
        )
        results = response.json()
        if not results:
            raise ValueError(f"Could not geocode: {raw_input}")
        return float(results[0]["lat"]), float(results[0]["lon"])

    @staticmethod
    def _reverse_geocode(lat, lng):
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lng, "format": "json"},
            headers={"User-Agent": NOMINATIM_USER_AGENT},
        )
        result = response.json()
        return result.get("address", {}).get("postcode")

    @staticmethod
    def _fuzz(lat, lng):
        FUZZ_MIN = 0.2
        FUZZ_MAX = 1.0
        MILES_PER_DEGREE = (
            69.0  # approx. miles per degree of latitude, constant everywhere
        )
        distance = random.uniform(FUZZ_MIN, FUZZ_MAX)
        angle = random.uniform(0, 2 * math.pi)
        delta = distance / MILES_PER_DEGREE
        fuzzed_lat = lat + delta * math.cos(angle)
        fuzzed_lng = lng + delta * math.sin(angle) / math.cos(math.radians(lat))
        # math.cos(math.radians(lat)) corrects longitude degrees for our latitude
        return round(fuzzed_lat, 6), round(fuzzed_lng, 6)

    # for making the map display
    def to_map_data(self):
        if self.location_type == "job":
            return {
                "lat": float(self.fuzzed_lat),
                "lng": float(self.fuzzed_lng),
                "display_radius_miles": 2,
            }
        elif self.location_type == "user":
            return {
                "lat": float(self.lat),
                "lng": float(self.lng),
                "search_radius_miles": self.search_radius_miles,
            }
