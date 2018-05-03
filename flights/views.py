from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.db.models import Q
from django.http import HttpResponse
from utils.response import remove_empty_lines
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm
from django.contrib.auth.models import User

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
    per_page = int(request.GET.get('per_page', 25))

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
    GET_dict = {key:value for key, value in request.GET.items()}
    GET_dict.pop('page', None)

    try:
        flights = paginator.page(page)
    except PageNotAnInteger:
        flights = paginator.page(1)
    except EmptyPage:
        flights = paginator.page(paginator.num_pages)

    return render(request,
        'flights/search_results.html',
        {
            'flights': flights,
            'request': request
        }
    )

def search_page(request):
    return render(request,
        'search_page.html',
        {}
    )

def flight_page(request, flight_id):
    return HttpResponse(Flight.objects.filter(id=flight_id).first())

def airport_page(request, airport_id):
    return HttpResponse(Airport.objects.filter(id=airport_id).first())

def plane_page(request, plane_id):
    return HttpResponse(Plane.objects.filter(name=plane_id).first())

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
