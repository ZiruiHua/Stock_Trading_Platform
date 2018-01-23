from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name='search'),
    url(r'^query/$', views.query, name='query'), #url(r'^query/([A-Za-z0-9 ]*)$', views.query, name='query'),
    url(r'^list/(?P<page>[0-9]*)$', views.get_stock_list, name='list'),
    url(r'^price/(?P<symbol>[A-Z.]+)$', views.get_stock_price, name='price'),
    url(r'filter/([0-9]+)/([A-Za-z]+)/([A-Za-z0-9.+]*)$', views.filter_stock_list, name='filter'),
]
