from django.conf.urls import url
from . import  views
from . import company_info_api 

urlpatterns = [
    url(r'^get-current-price/(?P<stock_symbol>\w*)$', views.query_current_price),
    url(r'^get-company-info/(?P<symbol>\w*)$', company_info_api.get_company_info),
]
