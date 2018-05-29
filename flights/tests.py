from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *

import json
import pytz
from datetime import datetime, timedelta

class FlightsTestCase(TestCase):
    fixtures = ['flights_tests.json']

    def setUp(self):
        user = User.objects.create_user(
            username='user',
            email='user@mail.com',
            password='pass'
        )
        user.save()

    def test_crew_api(self):
        crew = Crew(
            captain_firstname = 'Bruce',
            captain_lastname  = 'Wayne'
        )
        crew.save()
        response = self.client.get(reverse('ajax_get_crew'), {})
        self.assertEqual(response.status_code, 200)

        ret = json.loads(response.content)
        ret = [r for r in ret if r['id'] == crew.id]
        self.assertTrue(ret) # check if added crew is in returned json

        ret = ret[0]
        self.assertEqual(crew.id, ret['id'])
        self.assertEqual(crew.captain_firstname, ret['captain_firstname'])
        self.assertEqual(crew.captain_lastname, ret['captain_lastname'])

    def test_assign_crew_invalid_user(self):
        crew = Crew(
            captain_firstname = 'Bruce',
            captain_lastname  = 'Wayne'
        )
        crew.save()
        flight = Flight(
            plane        = Plane.objects.get(pk='Batman'),
            start_date   = datetime(1970, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(1970, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='WAW'),
            dest_airport = Airport.objects.get(pk='TXL')
        )
        flight.save()

        response = self.client.post(
            reverse('ajax_change_crew'),
            {
                'flight_id': flight.id,
                'crew_id': crew.id,
                'username': 'random_username',
                'password': 'random_password'
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_assign_crew_correct(self):
        crew = Crew(
            captain_firstname = 'Bruce',
            captain_lastname  = 'Wayne'
        )
        crew.save()
        flight = Flight(
            plane        = Plane.objects.get(pk='Batman'),
            start_date   = datetime(1970, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(1970, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='WAW'),
            dest_airport = Airport.objects.get(pk='TXL')
        )
        flight.save()

        response = self.client.post(
            reverse('ajax_change_crew'),
            {
                'flight_id': flight.id,
                'crew_id': crew.id,
                'username': 'user',
                'password': 'pass'
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_assign_crew_incorrect(self):
        crew = Crew(
            captain_firstname = 'Bruce',
            captain_lastname  = 'Wayne'
        )
        crew.save()
        flightA = Flight(
            plane        = Plane.objects.get(pk='Batman'),
            start_date   = datetime(1970, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(1970, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='WAW'),
            dest_airport = Airport.objects.get(pk='TXL')
        )
        flightA.save()
        flightB = Flight(
            plane        = Plane.objects.get(pk='Superman'),
            start_date   = datetime(1970, 1, 1, 1, 30, 0, tzinfo=pytz.UTC),
            end_date     = datetime(1970, 1, 1, 6, 30, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='TXL'),
            dest_airport = Airport.objects.get(pk='WAW')
        )
        flightB.save()

        response = self.client.post(
            reverse('ajax_change_crew'),
            {
                'flight_id': flightA.id,
                'crew_id': crew.id,
                'username': 'user',
                'password': 'pass'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('ajax_change_crew'),
            {
                'flight_id': flightB.id,
                'crew_id': crew.id,
                'username': 'user',
                'password': 'pass'
            }
        )
        self.assertEqual(response.status_code, 400)
