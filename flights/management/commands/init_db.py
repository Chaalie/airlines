from django.db import transaction
from django.core.management import BaseCommand, call_command

from flights.models import *

import pytz
import csv
import json
import random
import os
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Initiates and populates a database with data'
    aircrafts_names = []
    airports_data = {}
    aircrafts_data = {}
    firstnames = []
    surnames = []

    def handle(self, *args, **options):
        def clear_db():
            Country.objects.all().delete()
            City.objects.all().delete()
            Plane.objects.all().delete()
            Aircraft.objects.all().delete()
            Airport.objects.all().delete()
            Flight.objects.all().delete()
            Ticket.objects.all().delete()
            CrewMember.objects.all().delete()
            Crew.objects.all().delete()

        call_command('makemigrations')
        call_command('migrate')

        path = os.path.abspath(os.path.dirname(__file__))

        with open(os.path.join(path, 'data', 'aircraft_names.csv'), 'r') as f:
            names = next(csv.reader(f, delimiter=','))[0]
            aircrafts_names = [x for x in names.split(';') if x]
        with open(os.path.join(path, 'data', 'aircrafts.json'), 'r') as f:
            aircrafts_data = json.loads(f.read())
        with open(os.path.join(path, 'data', 'airports_eu.json'), 'r') as f:
            airports_data = json.loads(f.read())
        with open(os.path.join(path, 'data', 'firstnames.csv'), 'r') as f:
            names = csv.reader(f, delimiter=',')
            next(names)
            firstnames = [x[1].title() for x in names]
        with open(os.path.join(path, 'data', 'surnames.csv'), 'r') as f:
            names = csv.reader(f, delimiter=',')
            next(names)
            surnames = [x[1].title() for x in names]

        clear_db()
        with transaction.atomic():
            for country in airports_data.values():
                airport = country['airports'][0]
                country_obj = Country(
                    name = country['name'],
                    code = country['iso3']
                )
                country_obj.full_clean()
                country_obj.save()

                city_obj = City(
                    name    = airport['city'],
                    country = country_obj
                )
                city_obj.full_clean()
                city_obj.save()

                airport_obj = Airport(
                    id   = airport['iata'],
                    name = airport['name'],
                    city = city_obj
                )
                airport_obj.full_clean()
                airport_obj.save()

        with transaction.atomic():
            for aircraft in aircrafts_data:
                aircraft_obj = Aircraft(
                    producer = aircraft['producer'],
                    model    = aircraft['model'],
                    seats    = aircraft['seats']
                )
                aircraft_obj.full_clean()
                aircraft_obj.save()

        with transaction.atomic():
            def random_days(a, b):
                days = random.randint(a, b)
                return timedelta(days=days)

            def random_hours(a, b):
                hours = random.randint(a, b)
                return timedelta(hours=hours)

            def random_minutes():
                minutes = random.randint(0, 5)
                return timedelta(minutes=minutes*10)

            def random_elapsed_time(days_a=2, days_b=10, hours_a=0, hours_b=23):
                return random_days(days_a, days_b) + random_hours(hours_a, hours_b) + random_minutes()

            aircrafts = list(Aircraft.objects.all())
            airports = list(Airport.objects.all())
            for name in aircrafts_names:
                plane_obj = Plane(
                    name     = name,
                    aircraft = random.choice(aircrafts)
                )
                plane_obj.full_clean()
                plane_obj.save()

                flights_num = random.randint(50, 75)
                cities = random.choices(airports, k=flights_num+1)
                while any(i == j for i, j in zip(cities, cities[1:])):
                    random.shuffle(cities)

                connections = list(zip(cities[:-1], cities[1:]))
                start = datetime(2018, 1, 1, tzinfo=pytz.UTC)
                end = datetime(2018, 1, 1, tzinfo=pytz.UTC)
                for src, dest in connections:
                    start = end + random_elapsed_time()
                    end = start + random_hours(4, 10)
                    flight_obj = Flight(
                        plane        = plane_obj,
                        start_date   = start,
                        end_date     = end,
                        src_airport  = src,
                        dest_airport = dest
                    )
                    flight_obj.full_clean()
                    flight_obj.save()

        with transaction.atomic():
            crews_num = 50
            first_name = random.choices(firstnames, k=crews_num)
            last_name  = random.choices(surnames,   k=crews_num)
            for (f, l) in set(zip(first_name, last_name)):
                crew_obj = Crew(
                    captain_firstname = f,
                    captain_lastname = l
                )
                crew_obj.save()
                members_num = random.randint(2, 4)
                for _ in range(members_num):
                    fname = random.choice(firstnames)
                    lname = random.choice(surnames)
                    cm = CrewMember(
                        firstname = fname,
                        lastname = lname
                    )
                    cm.save()
                    crew_obj.members.add(cm)
                    crew_obj.save()
