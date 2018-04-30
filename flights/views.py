from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
import urllib
from django.db.models import Q

def flight_list(request):
    order = request.GET.get('order', 'start_date')
    page = request.GET.get('page', 1)
    phrase = request.GET.get('phrase', '')
    per_page = int(request.GET.get('per_page', 20))

    flight_list = Flight.objects.all().filter(
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

    return render_to_response(
        'flight_list.html',
        {
            'flights': flights,
            'request': request
        }
    )


#def flight_page(request, flight_id):

def search_page(request):
     return render_to_response(
         'search_page.html',
         {}
     )


