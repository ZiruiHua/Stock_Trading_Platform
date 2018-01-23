from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<stock_symbol>\w*)$', views.stock_view, name='stock_view'),
    url(r'^buy/$', views.buy_stock),
    url(r'^sell/$', views.sell_stock),
    url(r'^subscribe/$', views.subscribe),
    url(r'^unsubscribe/$', views.unsubscribe),
    url(r'^buying-power/$', views.buying_power),
]
