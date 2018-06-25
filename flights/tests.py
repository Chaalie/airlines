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
            start_date   = datetime(2020, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(2020, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
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
            start_date   = datetime(2020, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(2020, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
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
            start_date   = datetime(2020, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(2020, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='WAW'),
            dest_airport = Airport.objects.get(pk='TXL')
        )
        flightA.save()
        flightB = Flight(
            plane        = Plane.objects.get(pk='Superman'),
            start_date   = datetime(2020, 1, 1, 1, 30, 0, tzinfo=pytz.UTC),
            end_date     = datetime(2020, 1, 1, 6, 30, 0, tzinfo=pytz.UTC),
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

from django.test import StaticLiveServerTestCase
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver import ActionChains
import time

class FlightSeleniumTestCase(StaticLiveServerTestCase):
    fixtures = ['flights_tests.json']

    def setUp(self):
        user = User.objects.create_user(
            username='user',
            email='user@mail.com',
            password='pass',
        )
        user.first_name = 'Bruce'
        user.last_name = 'Wayne'
        user.save()
        flight = Flight(
            plane        = Plane.objects.get(pk='Batman'),
            start_date   = datetime(2020, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
            end_date     = datetime(2020, 1, 1, 6, 0, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='WAW'),
            dest_airport = Airport.objects.get(pk='TXL')
        )
        flight.save()
        flight = Flight(
            plane        = Plane.objects.get(pk='Superman'),
            start_date   = datetime(2020, 1, 1, 1, 30, 0, tzinfo=pytz.UTC),
            end_date     = datetime(2020, 1, 1, 6, 30, 0, tzinfo=pytz.UTC),
            src_airport  = Airport.objects.get(pk='TXL'),
            dest_airport = Airport.objects.get(pk='WAW')
        )
        flight.save()

        self.selenium = WebDriver()
        super(FlightSeleniumTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(FlightSeleniumTestCase, self).tearDown()

    def test_add_passenger(self):
        self.selenium.get(self.live_server_url)

        # login first
        self.selenium.find_element_by_name('username').send_keys('user')
        self.selenium.find_element_by_name('password').send_keys('pass')
        self.selenium.find_element_by_css_selector('input[type="submit"]').click()
        alert = self.selenium.find_element_by_class_name('alert')
        self.assertIn('alert-success', alert.get_attribute('class'))

        # move to flights menu and select first one
        self.selenium.find_element_by_link_text('Flights').click()
        self.selenium.find_element_by_link_text('1').click()

        # click 'Buy ticket' button and check if user shows up on list
        self.selenium.find_element_by_css_selector('input[value="Buy ticket"]').click()
        self.selenium.find_element_by_xpath('//*[@id="headingOne"]/button').click()
        name_td = self.selenium.find_element_by_xpath('//*[@id="collapseOne"]/div/table/tbody/tr/td[2]')
        self.assertEquals('Bruce Wayne', name_td.text)

    def test_crew_add(self):
        crew = Crew(
            captain_firstname = 'Bruce',
            captain_lastname  = 'Wayne'
        )
        crew.save()
        cm = CrewMember(
            firstname = 'Clark',
            lastname = 'Kent'
        )
        cm.save()
        crew.members.add(cm)
        crew.save()
        action_chains = ActionChains(self.selenium)
        self.selenium.get(self.live_server_url)

        # login first
        self.selenium.find_element_by_link_text('Crews').click()
        self.selenium.find_element_by_name('username').send_keys('user')
        self.selenium.find_element_by_name('password').send_keys('pass')
        self.selenium.find_element_by_xpath('//*[@id="login-form"]/input[3]').click()
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_class_name('alert')
        )
        alert = self.selenium.find_element_by_class_name('alert')
        self.assertIn('alert-success', alert.get_attribute('class'))

        # setup date of flights
        self.selenium.find_element_by_id('choose-date').send_keys('2020-01-01')
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_xpath('//*[@id="flights"]/tr[1]')
        )

        # double click on first flight
        row = self.selenium.find_element_by_xpath('//*[@id="flights"]/tr[1]')
        action_chains.double_click(row).perform()

        # choose first crew
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_xpath('//*[@id="select-crew"]/option[2]')
        )
        self.selenium.find_element_by_xpath('//*[@id="select-crew"]/option[2]').click()

        # send 'Change crew' and wait for change query to end
        self.selenium.find_element_by_xpath('//*[@id="crew-form"]/div[7]/input').click()
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_class_name('alert')
        )
        alert = self.selenium.find_element_by_class_name('alert')
        self.assertIn('alert-success', alert.get_attribute('class'))

        # refresh page and check if crew changed
        self.selenium.refresh()
        action_chains = ActionChains(self.selenium)
        self.selenium.find_element_by_id('choose-date').send_keys('2020-01-01')
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_xpath('//*[@id="flights"]/tr[1]')
        )
        new_crew = self.selenium.find_element_by_xpath('//*[@id="flights"]/tr[1]/td[6]/span[@class="captain"]')
        self.assertEquals('Bruce Wayne', new_crew.text)

        # double click on second flight
        row2 = self.selenium.find_element_by_xpath('//*[@id="flights"]/tr[2]')
        action_chains.double_click(row2).perform()

        # choose first crew
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_xpath('//*[@id="select-crew"]/option[2]')
        )
        self.selenium.find_element_by_xpath('//*[@id="select-crew"]/option[2]').click()

        # send 'Change crew' and wait for change query to end
        self.selenium.find_element_by_xpath('//*[@id="crew-form"]/div[7]/input').click()
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_class_name('alert')
        )
        alert = self.selenium.find_element_by_class_name('alert')
        self.assertIn('alert-danger', alert.get_attribute('class'))

        # check if crews didn't change
        self.selenium.refresh()
        self.selenium.find_element_by_id('choose-date').send_keys('2020-01-01')
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_xpath('//*[@id="flights"]/tr[1]')
        )
        crew1 = self.selenium.find_element_by_xpath('//*[@id="flights"]/tr[1]/td[6]/span[@class="captain"]')
        crew2 = self.selenium.find_element_by_xpath('//*[@id="flights"]/tr[2]/td[6]/span[@class="captain"]')
        self.assertEquals('Bruce Wayne', crew1.text)
        self.assertEquals('None', crew2.text)
