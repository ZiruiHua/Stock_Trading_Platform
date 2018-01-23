from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home_view, name='global'),
    url(r'^get-history-price/(?P<symbol>\w*)$', views.get_history_price, name='history_price'),
    url(r'^get-recommendation/$', views.get_recommendation_stocks, name='recommendations'),
]
