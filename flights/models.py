from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from pytz import timezone, UTC
from django.contrib.auth.models import User
from datetime import datetime
from django.shortcuts import get_object_or_404

class Country(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class City(models.Model):
    name    = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"


class Aircraft(models.Model):
    producer = models.CharField(max_length=64)
    model    = models.CharField(max_length=64)
    seats    = models.IntegerField()

    @property
    def name(self):
        return f'{self.producer} {self.model}'

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Aircraft"
        verbose_name_plural = "Aircrafts"
        unique_together = ('producer', 'model')


class Plane(models.Model):
    name     = models.CharField(max_length=64, primary_key=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)

    @property
    def seats(self):
        return self.aircraft.seats

    def __str__(self):
        return f'{self.name}, {self.aircraft.name}'

    class Meta:
        verbose_name = "Plane"
        verbose_name_plural = "Planes"


class Airport(models.Model):
    id   = models.CharField(max_length=3, primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.id} - {self.name}'

    @property
    def location(self):
        return f'{self.city}, {self.city.country}'

    def clean(self):
        if self.id == 'N/A':
            raise ValidationError(_('Starting date is earlier than the ending date!'))

    class Meta:
        verbose_name = "Airport"
        verbose_name_plural = "Airports"


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

    @property
    def seats(self):
        return self.plane.seats

    @property
    def available_seats(self):
        return self.seats - Ticket.objects.filter(flight=self.id).count()

    def __str__(self):
        return f'Flight: {self.connection} | {self.plane.name} | {self.start_date}/{self.end_date}'

    @property
    def start_date_pretty(self):
        return self.start_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def end_date_pretty(self):
        return self.end_date.astimezone(timezone('Poland')).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def finished(self):
        now = datetime.utcnow().replace(tzinfo=UTC)
        return self.end_date < now

    @property
    def in_air(self):
        now = datetime.utcnow().replace(tzinfo=UTC)
        return self.start_date < now and now < self.end_date

    @classmethod
    @transaction.atomic
    def buy_ticket(cls, flight_id, user):
        flight = get_object_or_404(cls.objects.select_for_update(), pk=flight_id)
        ticket = Ticket(flight=flight, passenger=user)
        ticket.clean()
        ticket.save()

    def clean(self):
        from datetime import timedelta
        if self.start_date > self.end_date:
            raise ValidationError(_('Starting date is earlier than the ending date!'))
        if timedelta(hours=4) > self.end_date - self.start_date:
            raise ValidationError(_('Flight should take at least 4 hours!'))
        if self.src_airport == self.dest_airport:
            raise ValidationError(_('Airports are not different!'))

    class Meta:
        verbose_name = "Flight"
        verbose_name_plural = "Flights"


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=False)
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def clean(self):
        if self.flight.in_air or self.flight.finished:
            raise ValidationError(_('Flight has already started!'))
        if self.flight.available_seats == 0:
            raise ValidationError(_('No seats available!'))

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
