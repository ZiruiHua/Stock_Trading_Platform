from django.contrib.auth.decorators import login_required
#from django.contrib.postgres.search import SearchQuery, SearchVector
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from os.path import normpath, join

from MockInternetTraderSite.settings import *
from global_resources.models import *

import csv
import json
import requests


# Disable decorators for testing
@login_required
def search(request):
    return render(request, 'search/stock_search.html', {})

@login_required
def query(request):
    if request.method == 'GET':
        query = request.GET['query']
        query_terms = query.split()
        results = []
        for q in query_terms:
            results.extend(Stock.objects.filter(symbol__icontains=q))
            results.extend(Stock.objects.filter(name__icontains=q))
        for q in query_terms:
            results.extend(Stock.objects.filter(company_description__icontains=q))
        return render(request, 'search/search_results.html', {'query': query, 'results': results})
    else:
        raise Http404("Search failed.")


@login_required
def get_stock_list(request, page=0):
    print(page)
    if request.method == 'GET':
        if page == '':
            page = 0
        json_output = []
        lb = int(page) * 20
        stock_page = Stock.objects.all()[lb:lb+20]
        for s in stock_page:
            company_info = {'symbol': s.symbol,
                            'name': s.name,
                            'sector': s.company_description,
                            'industry': ''}
            json_output.append(company_info)
        stocks = {'stocks': json_output}
        return JsonResponse(stocks)
    else:
        raise Http404("Search failed.")


@login_required
def get_stock_price(request, symbol):
    api_key = 'Z3LPQXNRS2N4QKBT'  # TODO: obscure api_key
    r = requests.get(
        'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + symbol + '&interval=1min&apikey=' + api_key)
    intraday = r.json()
    try:
        last_refreshed = intraday['Meta Data']['3. Last Refreshed']
        price = intraday['Time Series (1min)'][last_refreshed]['4. close']
    except:
        raise Http404("Price retrieval failed.")
    return HttpResponse(price)

@login_required
def filter_stock_list(request, page, filter, terms):
    if request.method == 'GET':
        if page == '':
            page = 0
        lb = int(page) * 20
        ub = (int(page) + 1) * 20
        filter_terms = terms.split('+')
        json_output = []
        stock_page = []
        for t in filter_terms:
            if filter == "symbol":     
                stock_page.extend(Stock.objects.filter(symbol__icontains=t))
            elif filter == "name":
                stock_page.extend(Stock.objects.filter(name__icontains=t))
            elif filter == "sector":
                stock_page.extend(Stock.objects.filter(company_description__icontains=t))
            elif filter == "industry":
                stock_page = []
            else:
                return get_stock_list(request, page)
        for s in stock_page:
            company_info = {'symbol': s.symbol,
                            'name': s.name,
                            'sector': s.company_description,
                            'industry': ''}
            json_output.append(company_info)
        stocks = {'stocks': json_output}
        return JsonResponse(stocks)
    else:
        raise Http404("Search failed.")
