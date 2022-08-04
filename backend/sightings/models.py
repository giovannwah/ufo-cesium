from django.db import models
from django.contrib.auth.models import User


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
    longitude = models.DecimalField(max_digits=17, decimal_places=14)
    latitude = models.DecimalField(max_digits=17, decimal_places=14)

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

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    sighting_datetime = models.DateTimeField()
    # Meta info
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Date: {0}, Location: {1}' \
            .format(self.sighting_datetime, self.location.__str__(),)


class Post(models.Model):
    """
    Model representing a particular post made by a user
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sighting = models.ForeignKey(Sighting, on_delete=models.CASCADE)
    ufo_shape = models.CharField(max_length=16, choices=Shape.choices, default=Shape.UNKNOWN)
    duration = models.CharField(max_length=32, default=None)
    description = models.CharField(max_length=1028, default=None)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}: Post {1}'.format(self.user.username, self.pk)


class Profile(models.Model):
    """
    Model representing a user's profile information
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(Post, blank=True)

    def __str__(self):
        return self.user.username
