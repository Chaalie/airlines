from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
#    path('', views.main_page, name='main_page'),
    path('flights/', views.flight_list, name='flight_list'),
    path('search/', views.search_page, name='search_page'),
#    path('flights/<int:flight_id>', views.flight_info, name='flight_page'),
]
