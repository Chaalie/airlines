from django.contrib import admin
from .models import *

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Airport)
admin.site.register(Aircraft)
admin.site.register(Plane)
admin.site.register(Crew)

# Register your models here.
