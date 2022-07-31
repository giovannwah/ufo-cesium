"""
Create JSON fixtures from csv files containing ufo sighting info
"""
import os
import sys
import typer
import csv
import json

from datetime import datetime

# Maximum longitude/latitude difference for locations to be considered identical
LOCATION_THRESHOLD = 0.001

app = typer.Typer()

location_model = 'sightings.location'
sighting_model = 'sightings.sighting'

locations = set()


def fixture_object(pk, model, row):
    """
    Build dict from data row representing fixture object of the given model type.
    """
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
                'longitude': float(row['city_longitude']),
                'latitude': float(row['city_latitude']),
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
                'location': row['loc_pk'],
                'sighting_datetime': row['date_time'],
                'created_datetime': now,
                'modified_datetime': now
            }
        }


def compare_loc(loc1, loc2):
    """
    Compare two locations, (latitude: str, longitude: str), to determine if they are close
    enough to be considered the same location
    """
    if abs(float(loc1[0]) - float(loc2[0])) < LOCATION_THRESHOLD and \
        abs(float(loc1[1]) - float(loc2[1])) < LOCATION_THRESHOLD:
        return True
    return False


def search_location(loc, threshold=False):
    """
    Search for location, (latitude: str, longitude: str), in locations array.
    :param loc: location tuple
    :param threshold: whether to apply threshold to location comparison
    :return:
    """
    if threshold:
        l = [x for x in locations if compare_loc(x, loc)]
    else:
        l = [x for x in locations if x[0] == loc[0] and x[1] == loc[1]]
    if len(l) == 0:
        return None
    return l[0]


def get_location_pk(loc):
    """
    Search for private key of given location (loc) in locations list
    """
    l = search_location(loc)
    if l:
        return l[2]
    return l


@app.command()
def build_fixture(input_path: str, fixture_name: str):
    """
    Build fixture object from input csv file
    """
    total = 0
    current = 0
    count = 0
    if not os.path.exists(input_path):
        print(f'Error: Path does not exist ({input_path}).')
        sys.exit(1)
    else:
        fixture = []
        with open(input_path, 'r') as file:
            reader = csv.DictReader(file)
            for _ in reader:
                # count total rows
                total += 1
            print(f'{total} total rows. Processing.')

        with open(input_path, 'r') as file:
            reader = csv.DictReader(file)
            location_pk = 1
            sighting_pk = 1
            for row in reader:
                current += 1
                if not row['city_latitude'] or not row['city_longitude'] or not row['date_time']:
                    # skip sightings with no latitude/longitude
                    continue
                count += 1
                loc = (row['city_latitude'], row['city_longitude'], location_pk)
                is_dupe = search_location(loc, True)

                if not is_dupe:
                    locations.add(loc)
                    fixture.append(fixture_object(location_pk, location_model, row))
                    row['loc_pk'] = location_pk
                    location_pk += 1
                    fixture.append(fixture_object(sighting_pk, sighting_model, row))
                    sighting_pk += 1
                else:
                    lpk = get_location_pk(loc)
                    if lpk:
                        row['loc_pk'] = lpk
                        fixture.append(fixture_object(sighting_pk, sighting_model, row))
                        sighting_pk += 1

                if current % 2000 == 0:
                    print(f'{round(current/total * 100, 3)}% complete')

            # sort fixture by location objects first
            fixture = sorted(fixture, key=lambda o: o['model'])

        print(f'Processed {count} total rows.')
        with open(fixture_name, 'w') as out:
            json.dump(fixture, out)


@app.command()
def count_null_locations(input_path: str):
    """
    Determine how many rows in the input file are missing longitude/latitude data
    """
    missing = 0
    total = 0
    with open(input_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row['city_latitude'] or not row['city_longitude']:
                missing += 1
            total += 1
        print('No missing locations.' if not missing else f'Total "missing" locations: {missing}/{total}')


@app.command()
def count_duplicates(input_path: str):
    """
    Determine how many rows in the input file have duplicated locations
    """
    dupes = 0
    total = 0
    if not os.path.exists(input_path):
        print(f'Error: Path does not exist ({input_path}).')
        sys.exit(1)
    else:
        with open(input_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                loc = (row['city_latitude'], row['city_longitude'], )
                if not loc[0] or not loc[1]:
                    continue
                total += 1
                if search_location(loc, True):
                    dupes += 1
                else:
                    locations.add(loc)
    print('No duplicates.' if not dupes else f'Total duplicates: {dupes}/{total}, Threshold: {LOCATION_THRESHOLD}')


if __name__ == '__main__':
    app()
