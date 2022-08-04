import django

django.setup()


def make_posts():
    from django.contrib.auth.models import User
    from sightings.models import Sighting, Post

    sightings = Sighting.objects.all()
    user = User.objects.filter(username='admin').first()
    for sighting in sightings:
        post = Post(
            sighting=sighting,
            user=user,
            ufo_shape=sighting.ufo_shape,
            duration=sighting.duration,
            description=sighting.description,
        )
        post.save()


if __name__ == '__main__':
    make_posts()
