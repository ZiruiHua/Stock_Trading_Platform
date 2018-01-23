from django.conf.urls import url
from . import  views

urlpatterns = [
    url(r'^get-holdings/$', views.get_holdings),
    url(r'^get-trend/$', views.get_trend),
    url(r'^personal-dashboard/$', views.render_personal_dashboard,name='personal_home2'),
    url(r'^$', views.render_personal_dashboard, name='personal_home'),
    url(r'^get-transactions/$', views.get_transactions),
    url(r'^get-holdings/$', views.get_holdings),
    url(r'^get-trend/$', views.get_trend),
    url(r'^get-transactions-by-date/(?P<date>.*)$', views.getTransactionsByDate, name='getTransactionsByDate'),
]