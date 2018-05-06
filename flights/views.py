from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .forms import RegistrationForm
from .models import *

from utils.response import remove_empty_lines

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
