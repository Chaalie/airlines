from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from pytz import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class Country(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return f'{self.name}'

class City(models.Model):
    name    = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

class Aircraft(models.Model):
    producer = models.CharField(max_length=64)
    model    = models.CharField(max_length=64)
    seats    = models.IntegerField()

    class Meta():
        unique_together = ('producer', 'model')

    @property
    def name(self):
        return f'{self.producer} {self.model}'

    def __str__(self):
        return f'{self.name}'

class Plane(models.Model):
    name     = models.CharField(max_length=64, primary_key=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)

    @property
    def seats(self):
        return self.aircraft.seats

    def __str__(self):
        return f'{self.name}, {self.aircraft.name}'

class Airport(models.Model):
    id   = models.CharField(max_length=3, primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.id} - {self.name}'

    def clean(self):
        if self.id == 'N/A':
            raise ValidationError(_('Starting date is earlier than the ending date!'))


class Flight(models.Model):
 #   flight_id   = models.IntegerField(primary_key=True)
    plane        = models.ForeignKey(Plane, on_delete=models.CASCADE)
    start_date   = models.DateTimeField()
    end_date     = models.DateTimeField()
    src_airport  = models.ForeignKey(Airport, related_name="src_airport", on_delete=models.CASCADE)
    dest_airport = models.ForeignKey(Airport, related_name="dest_airport", on_delete=models.CASCADE)

    @property
    def connection(self):
        return f'{self.src_airport.id}-{self.dest_airport.id}'

    def __str__(self):
        return f'Flight: {self.connection} | {self.plane.name} | {self.start_date}/{self.end_date}'

    @property
    def start_date_pretty(self):
        return self.start_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def end_date_pretty(self):
        return self.end_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")

    def clean(self):
        from datetime import timedelta
        if self.start_date > self.end_date:
            raise ValidationError(_('Starting date is earlier than the ending date!'))
        if timedelta(hours=4) > self.end_date - self.start_date:
            raise ValidationError(_('Flight should take at least 4 hours!'))
        if self.src_airport == self.dest_airport:
            raise ValidationError(_('Airports are not different!'))


# class User(AbstractUser):
#     firstname = models.CharField(max_length=64)
#     lastname  = models.CharField(max_length=64)

#     def clean(self):
#         cleaned_data = super().clean()


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.flight.ticket_set.count() == self.flight.plane.seats:
            raise ValidationError(_('No seats available!'))
