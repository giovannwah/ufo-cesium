import os
import sys
import typer
import csv
import json

from datetime import datetime

"""
Create JSON fixtures from csv files containing ufo sighting info
"""

app = typer.Typer()

location_model = 'sightings.location'
sighting_model = 'sightings.sighting'

locations = []


def fixture_object(pk, model, row):
    if model == location_model:
        # parse out city/state/country, handle location objects
        country = ''
        state = row['state']
        if state.strip():
            country = 'United States'
            city = row['city']
        else:
            i = row['city'].find('(')
            j = row['city'].find(')')
            if i > -1 and j > -1:
                city = row['city'][:i - 1]
                country = row['city'][i + 1:j]
            else:
                city = row['city']
        return {
            'pk': pk,
            'model': model,
            'fields': {
                'longitude': row['city_longitude'],
                'latitude': row['city_latitude'],
                'city': city,
                'state': state,
                'country': country
            }
        }
    else:
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        return {
            'pk': pk,
            'model': model,
            'fields': {
                'ufo_shape': row['shape'] or 'unknown',
                'duration': row['duration'],
                'description': row['summary'],
                'location': [row['city_longitude'], row['city_latitude']],
                'sighting_datetime': row['date_time'],
                'created_by_user': 1,
                'created_datetime': now,
                'modified_datetime': now
            }
        }


def search_location(loc):
    l = [x for x in locations if x[0] == loc[0] and x[1] == loc[1]]
    return l[0]


@app.command()
def build_fixture(input_path: str, fixture_name: str):
    if not os.path.exists(input_path):
        print(f'Error: Path does not exist ({input_path}).')
        sys.exit(1)
    else:
        fixture = []
        with open(input_path, 'r') as file:
            reader = csv.DictReader(file)
            location_pk = 1
            sighting_pk = 1
            for row in reader:
                loc = (row['city_latitude'], row['city_longitude'])
                if loc not in locations:
                    locations.append(loc)
                    fixture.append(fixture_object(location_pk, location_model, row))
                    location_pk += 1
                fixture.append(fixture_object(sighting_pk, sighting_model, row))
                sighting_pk += 1

        with open(fixture_name, 'w') as out:
            json.dump(fixture, out)


if __name__ == '__main__':
    app()
