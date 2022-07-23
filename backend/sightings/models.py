from django.db import models
from django.conf import settings


class LocationManager(models.Manager):
    def get_by_natural_key(self, longitude, latitude):
        return self.get(longitude=longitude, latitude=latitude)


class Location(models.Model):
    """
    Model representing a particular geographical location
    """
    class State(models.TextChoices):
        ALABAMA = 'AL'
        ALASKA = 'AK'
        ARIZONA = 'AZ'
        ARKANSAS = 'AR'
        CALIFORNIA = 'CA'
        COLORADO = 'CO'
        CONNECTICUT = 'CT'
        DELAWARE = 'DE'
        FLORIDA = 'FL'
        GEORGIA = 'GA'
        HAWAII = 'HI'
        IDAHO = 'ID'
        ILLINOIS = 'IL'
        INDIANA = 'IN'
        IOWA = 'IA'
        KANSAS = 'KS'
        KENTUCKY = 'KY'
        LOUISIANA = 'LA'
        MAINE = 'ME'
        MARYLAND = 'MD'
        MASSACHUSETTS = 'MA'
        MICHIGAN = 'MI'
        MINNESOTA = 'MN'
        MISSISSIPPI = 'MS'
        MISSOURI = 'MO'
        MONTANA = 'MT'
        NEBRASKA = 'NE'
        NEVADA = 'NV'
        NEW_HAMPSHIRE = 'NH'
        NEW_JERSEY = 'NJ'
        NEW_MEXICO = 'NM'
        NEW_YORK = 'NY'
        NORTH_CAROLINA = 'NC'
        NORTH_DAKOTA = 'ND'
        OHIO = 'OH'
        OKLAHOMA = 'OK'
        OREGON = 'OR'
        PENNSYLVANIA = 'PA'
        RHODE_ISLAND = 'RI'
        SOUTH_CAROLINA = 'SC'
        SOUTH_DAKOTA = 'SD'
        TENNESSEE = 'TN'
        TEXAS = 'TX'
        UTAH = 'UT'
        VERMONT = 'VT'
        VIRGINIA = 'VA'
        WASHINGTON = 'WA'
        WEST_VIRGINIA = 'WV'
        WISCONSIN = 'WI'
        WYOMING = 'WY'

    state = models.CharField(max_length=2, choices=State.choices, default=None)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)

    objects = LocationManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['longitude', 'latitude'], name='unique_location'),
        ]

    def __str__(self):
        s = '{0}, {1}'.format(self.state, self.country) if self.state else '{0}'.format(self.country)
        return '{0}, {1} (lat: {2}, lon: {3})'.format(self.city, s, self.latitude, self.longitude)


class Sighting(models.Model):
    """
    Model representing a particular UFO sighting at a particular time and place
    """
    class Shape(models.TextChoices):
        CHANGING = 'changing'
        CHEVRON = 'chevron'
        CIGAR = 'cigar'
        CIRCLE = 'circle'
        CONE = 'cone',
        CRESCENT = 'crescent'
        CROSS = 'cross'
        CYLINDER = 'cylinder'
        DELTA = 'delta'
        DIAMOND = 'diamond'
        DISK = 'disk'
        EGG = 'egg'
        FIREBALL = 'fireball'
        FLASH = 'flash'
        FORMATION = 'formation'
        LIGHT = 'light'
        OTHER = 'other'
        OVAL = 'oval'
        PYRAMID = 'pyramid'
        RECTANGLE = 'rectangle'
        ROUND = 'round'
        SPHERE = 'sphere'
        TEARDROP = 'teardrop'
        TRIANGLE = 'triangle'
        UNKNOWN = 'unknown'

    ufo_shape = models.CharField(max_length=16, choices=Shape.choices, default=Shape.UNKNOWN)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    duration = models.CharField(max_length=32)
    sighting_datetime = models.DateTimeField()
    description = models.CharField(max_length=1028)
    # Meta info
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return 'Date: {0}\nLocation: {1}\nDuration: {2}\nShape: {3}\nUser: {4}' \
            .format(self.sighting_datetime, self.location.__str__(), self.duration, self.ufo_shape,
                    self.created_by_user.__str__())
