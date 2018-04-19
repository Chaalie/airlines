from django.db import models

class Country(models.Model):
    name       = models.CharField(max_length=64)
    country_id = models.CharField(max_length=3, primary_key=True)

class City(models.Model):
    name       = models.CharField(max_length=64)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE)

class Aircraft(models.Model):
    producer = models.CharField(max_length=64)
    model    = models.CharField(max_length=64)
    seats    = models.IntegerField()

    class Meta():
        unique_together = ('producer', 'model')

    @property
    def name(self):
        return f'{self.producer} {self.model}'

class Plane(models.Model):
    name        = models.CharField(max_length=64, primary_key=True)
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.CASCADE)

class Airport(models.Model):
    id      = models.CharField(max_length=3, primary_key=True)
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    name    = models.CharField(max_length=128)

class Flight(models.Model):
 #   flight_id   = models.IntegerField(primary_key=True)
    plane_id    = models.ForeignKey(Plane, on_delete=models.CASCADE)
    start_date  = models.DateTimeField()
    end_date    = models.DateTimeField()
    src_airport = models.ForeignKey(Airport, related_name="src_airport", on_delete=models.CASCADE)
    dest_airport = models.ForeignKey(Airport, related_name="dest_airport", on_delete=models.CASCADE)

    @property
    def airports(self):
        return f'{self.src_airport}-{self.dst_airport}'

    def __str__(self):
        return f'Flight: {self.airports} | {self.start_date}/{self.end_date}'

class Passenger(models.Model):
    flight_id  = models.ForeignKey(Flight, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64)
    last_name  = models.CharField(max_length=64)
