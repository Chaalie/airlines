from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.core.serializers import serialize

from .forms import RegistrationForm
from .models import *

from utils.response import remove_empty_lines
import pytz

@remove_empty_lines
def main_page(request):
    return render(request, 'main_page.html', {})

@remove_empty_lines
def flight_list(request):
    ORDER_CHOICES = {
        'id': 'id',
        'start': 'start_date',
        'end': 'end_date',
        'src': 'src_airport',
        'dest': 'dest_airport',
        'plane': 'plane__name'
    }
    order = request.GET.get('order', 'start')
    if not order in ORDER_CHOICES:
        order = 'start'
    order = ORDER_CHOICES[order]
    page = request.GET.get('page', 1)
    phrase = request.GET.get('phrase', '')
    per_page = int(request.GET.get('per_page', 10))

    flight_list = Flight.objects.filter(
         Q(plane__name__contains=phrase) |
         Q(src_airport__id__contains=phrase) |
         Q(dest_airport__id__contains=phrase) |
         Q(src_airport__name__contains=phrase) |
         Q(dest_airport__name__contains=phrase) |
         Q(src_airport__city__name__contains=phrase) |
         Q(dest_airport__city__name__contains=phrase)
     )
    flight_list = flight_list.order_by(order)

    paginator = Paginator(flight_list, per_page)

    try:
        flights = paginator.page(page)
    except PageNotAnInteger:
        flights = paginator.page(1)
    except EmptyPage:
        flights = paginator.page(paginator.num_pages)

    return render(
        request,
        'flights/content.html',
        {
            'flights': flights,
            'request': request
        }
    )

@remove_empty_lines
def flight_page(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    tickets = Ticket.objects.filter(flight=flight_id)

    return render(
        request,
        'flights/flight_page/content.html',
        {
            'flight': flight,
            'tickets': tickets,
        }
    )

@require_POST
def login_view(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        messages.success(request, 'You were successfully logged in!')
    else:
        messages.error(request, 'Login failed! Please, try again.')

    return redirect(request.GET['redirect'])

def logout_view(request):
    if request.user.is_authenticated:
        auth_logout(request)
        messages.success(request, 'You have successfully logged out!')
    else:
        messages.error(request, 'You are not logged in!')
    return redirect(request.GET['redirect'])

@remove_empty_lines
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account was successfully register! You can now log in.')
            return redirect('flight_list')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})

@require_POST
def buy_ticket(request, flight_id):
    try:
        if request.user.is_authenticated:
            Flight.buy_ticket(flight_id, request.user)
            messages.success(request, 'You have successfully bought a ticket!')
        else:
            raise ValidationError(_('You have to be login in to buy a ticket!'))
    except ValidationError:
        messages.error(request, 'Whoops! Something went wrong...')
    return redirect(request.GET['redirect'])

def airport_page(request, airport_id):
    obj = get_object_or_404(Airport, id=airport_id)
    return HttpResponse(obj)

def plane_page(request, plane_id):
    obj = get_object_or_404(Plane, name=plane_id)
    return HttpResponse(obj)

@require_POST
@csrf_exempt
def ajax_change_crew(request):
    if any(s not in request.POST for s in ['flight_id', 'crew_id', 'username', 'password']):
        return HttpResponse('', status=400)
    if not authenticate(username=request.POST['username'], password=request.POST['password']):
        raise PermissionDenied

    try:
        int(request.POST['flight_id'])
        int(request.POST['crew_id'])
    except ValueError:
        return HttpResponse('', status=400)

    fli = get_object_or_404(Flight, id=request.POST['flight_id'])
    crw = get_object_or_404(Crew, id=request.POST['crew_id'])
    try:
        with transaction.atomic():
            fli.crew = crw
            fli.full_clean()
            fli.save()
    except ValidationError as e:
        return HttpResponse('', status=400)

    return HttpResponse('OK')

@require_GET
@csrf_exempt
def ajax_get_flight(request):
    objs = Flight.objects.all()
    if 'date' in request.GET:
        try:
            tz = pytz.timezone('Europe/Warsaw')
            frm = tz.localize(datetime.strptime(request.GET['date'], '%Y-%m-%d'))
            to = frm + timedelta(days=1)
            objs = objs.filter(start_date__gte=frm, start_date__lt=to).order_by('start_date')
        except:
            return HttpResponse('', status=404)
    if 'id' in request.GET:
        ids = list(request.GET['id'].split(','))
        objs = objs.filter(pk__in=ids)
    flights = []
    for f in objs:
        flights.append({
            'id': f.id,
            'departure_airport': str(f.src_airport),
            'departure_date': f.start_date_pretty,
            'arrival_airport': str(f.dest_airport),
            'arrival_date': f.end_date_pretty,
            'captain': str(f.crew),
        })

    return JsonResponse(flights, safe=False, json_dumps_params={'indent': 4})

@require_GET
@csrf_exempt
def ajax_get_crew(request):
    objs = Crew.objects.all()
    if 'id' in request.GET:
        ids = list(request.GET['id'].split(','))
        objs = objs.filter(pk__in=ids)

    crews = []
    for c in objs:
        crews.append({
            'id': c.id,
            'captain_firstname': c.captain_firstname,
            'captain_lastname': c.captain_lastname,
        })

    return JsonResponse(crews, safe=False, json_dumps_params={'indent': 4})

@require_GET
@csrf_exempt
def ajax_login(request):
    if any(s not in request.GET for s in ['username', 'password']):
        raise PermissionDenied

    if authenticate(username=request.GET['username'], password=request.GET['password']):
        return HttpResponse('OK')
    else:
        raise PermissionDenied
