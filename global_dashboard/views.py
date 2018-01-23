import datetime
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from apis.alpha_vantage_api import get_historical_prices
from global_resources.exceptions import Http400Error
from global_resources.models import TotalAsset, Trade, HoldingHistory, Account

logger = logging.getLogger(__name__)


@login_required
def home_view(request):

    # update HoldingHistory
    try:
        user_account = Account.objects.get(owner=request.user)
    except:
        raise Http404

    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    HoldingHistory.fill_the_gap(user_account, today)

    # get the records of the top 20 users that have the most assets after market closed yesterday
    TotalAsset.fill_the_gap(account=user_account, date=today)
    leaders = TotalAsset.objects.filter(date=yesterday).order_by('-total_asset')[:20]
    context = {
        'records': Trade.objects.all().order_by('-date'),
        'leaders': leaders,
        'symbols': get_watch_list(request.user)
    }

    return render(request, 'global_dashboard/global.html', context)


def get_history_price(request, symbol):
    context = {}
    try:
        # get the current price
        prices = get_historical_prices(symbol, 5)

        keys = list(prices.keys())
        keys = list(reversed(keys))
        date = []
        price = []
        for i in range(5):
            date_cur = keys[i]
            price_cur = prices[date_cur]
            date.append(date_cur[5:])  # only display month and day
            price.append(price_cur)
        # prices, dates, symbol (str)
        context['p'] = price
        context['d'] = date
        context['s'] = symbol

    except Http400Error as err:
        logger.error('400: ' + err.message)

    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')


def get_recommendation_stocks(request):


    symbols = get_watch_list(request.user)
    context = {
        'symbols': symbols
    }
    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')


def get_watch_list(owner):
    try:
        account = get_object_or_404(Account, owner=owner)
    except:
        raise Http404("No such user")
    symbols = []
    watched_stocks = account.watched_stocks.values_list("symbol", flat=True).distinct()
    for stock in watched_stocks:
        symbols.append(stock)

    return symbols