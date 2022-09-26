# UFO-CESIUM

## Overview
UFO Cesium is a small web app allowing registered users to view, search for, and record new ufo sightings from all around the world. Built using 
Django, Strawberry-Graphql.

## Getting Started

### Requirements
- Docker Compose v1.29.0+ 
- Docker v20.10.0+

### Installation

After cloning the repo,
1. Fill in the required values in the .env file.
2. Run `docker-compose up` to build the images and bring up the containers.
3. Go to `localhost:<BACKEND_PORT>/api` to access the graphql UI.

__Load Base Data__

1) Assuming a fresh volume exists, and you want to load the base data fixture, run `docker exec -it <backend container id> bash`.
2) Run `python manage.py migrate`.
3) Run `python manage.py clearcontenttypes` to clear the content types table.
4) Run `python manage.py loaddata sightings/fixtures/nuforc_base_data.json`

## Data

__Making New Fixtures__
- `python scripts/make-fixture.py <input_csv> <output_json>`
- Ex: `python scripts/make-fixture.py ~/nufoc/nuforc_reports.csv nuforc_fixture.json`
- Currently only works with .csv data formatted similarly to data in the following source: https://data.world/timothyrenner/ufo-sightings/workspace/file?filename=nuforc_reports.csv