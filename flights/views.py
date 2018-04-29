from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *

def flight_list(request):
    order = request.GET.get('order', 'start_date')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 20))

    flight_list = Flight.objects.all().order_by(order)
    paginator = Paginator(flight_list, per_page)

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


