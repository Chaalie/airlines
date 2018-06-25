from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Flight, Crew

class FlightConsumer(JsonWebsocketConsumer):

    def get_data(self):
        def get_crews():
            objs = Crew.objects.prefetch_related('members').all()
            crews = {}
            for c in objs:
                members = []
                for m in c.members.all():
                    members.append({
                        'firstname': m.firstname,
                        'lastname': m.lastname
                    })
                crews[c.id] = {
                    'id': c.id,
                    'captain_firstname': c.captain_firstname,
                    'captain_lastname': c.captain_lastname,
                    'members': members,
                }
            return crews

        def get_flights():
            objs = Flight.objects.select_related('src_airport', 'dest_airport').all()
            flights = {}
            for f in objs:
                flights[f.id] = {
                    'id': f.id,
                    'departure_airport': str(f.src_airport),
                    'departure_date': f.start_date_pretty,
                    'arrival_airport': str(f.dest_airport),
                    'arrival_date': f.end_date_pretty,
                    'crew_id': f.crew.id if f.crew is not None else None,
                }
            return flights

        return {'flights': get_flights(), 'crews': get_crews()}


    def connect(self):
        self.accept()

    def receive_json(self, content):
        print('RECEIVE %s' % str(content))

        if content['type'] == 'login':
            self.login(content)

        elif content['type'] == 'sync':
            self.sync(content)

        elif content['type'] == 'get':
            self.get(content)

    def login(self, content):
        if all(s in content for s in ['username', 'password']) and authenticate(username=content['username'], password=content['password']):
            self.send_json({'type': 'login'})
        else:
            self.send_json({'type': 'login', 'error': 'Invalid username or password'})

    @transaction.atomic()
    def sync(self, content):
        if any(s not in content for s in ['username', 'password']) or not authenticate(username=content['username'], password=content['password']):
            self.send_json({
                **{
                    'type': 'sync',
                    'error': 'login'
                }, **self.get_data()
            })
            return

        verified = {}
        to_save = []

        try:
            with transaction.atomic():
                for k, v in content['data'].items():
                    try:
                        fli = Flight.objects.get(id=k)
                        crw = Crew.objects.get(id=v['new'])
                        crw_old = None
                        if v['old'] is not None:
                            crw_old = Crew.objects.get(id=v['old'])

                        if v['old'] == v['new'] or crw_old != fli.crew:
                            verified[k] = 'wrong'
                            continue

                        fli.crew = crw
                        fli.full_clean()
                        fli.save()
                        to_save.append(fli)
                        verified[k] = 'ok'
                    except Exception as e:
                        verified[k] = 'wrong'

                if all(v == 'ok' for k, v in verified.items()):
                    self.send_json({**{'type': 'sync'}, **self.get_data()})
                else:
                    self.send_json({
                        **{
                            'type': 'sync',
                            'error': 'changes',
                            'verified': verified
                        }, **self.get_data()
                    })
                    # in case of wrong changes, make sure that data won't be commited
                    # by raising an error (kinda hacky)
                    raise ValidationError('Error')
        except:
            pass

    def get(self, content):
        data = self.get_data()
        data['type'] = 'get'
        self.send_json(data)

    def disconnect(self, code):
        print('DISCONNECT')
