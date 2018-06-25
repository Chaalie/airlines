from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from flights.consumers import FlightConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
                path('crews/', FlightConsumer),
    ]),
    # http handled by Django as usual
})
