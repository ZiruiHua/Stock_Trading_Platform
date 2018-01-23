from django.shortcuts import render, redirect, get_object_or_404
from global_resources.models import *
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.core import serializers
from django.utils import timezone
import datetime
import json
from apis.alpha_vantage_api import get_current_price


# get the current user's holding info
@login_required
def get_holdings(request):
    context = {}
    symbol_list = []
    value_list = []
    share_list = []
    stock_value = 0
    indicator_list = []
    try:
        account = get_object_or_404(Account, owner=request.user)
    except:
        raise Http404("No such user")
    try:
        holds = Hold.objects.filter(account=account)
    except:
        raise Http404("No such account")
    if not holds:
        context['total_asset'] = format(float(account.buying_power), '.2f')
        data = json.dumps(context)
        return HttpResponse(data, content_type='application/json')
    for hold in holds:
        symbol = hold.stock.symbol
        symbol_list.append(symbol)
        today = datetime.date.today()
        today = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
        # record = get_object_or_404(stockHistory, symbol=symbol, date=today)
        records = StockHistory.objects.filter(symbol=symbol, date=today)
        # today's price of that stock has already been queried before
        if records:
            price = records.first().price
        else:
            # if not, query by API and write into db
            price = get_current_price(symbol)
            new_record = StockHistory(symbol=symbol, date=today, price=price)
            new_record.save()

        share = hold.shares
        amount = float(price * share)
        stock_value += amount
        # if current price is higher than the average cost, if so, indicating earning money
        if (price > hold.average_cost):
            indicator_list.append(1)
        elif (price < hold.average_cost):
            indicator_list.append(-1)
        else:
            indicator_list.append(0)

        share_list.append(share)
        value_list.append(amount)

    asset_sum = float(stock_value) + float(account.buying_power)
    asset_sum = format(asset_sum, '.2f')
    context['total_asset'] = asset_sum
    context['symbol_list'] = symbol_list
    context['value_list'] = value_list
    context['share_list'] = share_list
    context['indicator_list'] = indicator_list
    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')

# list all transactions belong to that account
# table form: stock_name|buy or se ll|price|share|
@login_required
def get_transactions(request):
    context = []
    try:
        account = get_object_or_404(Account, owner=request.user)
    except:
        raise Http404("No such user")
    try:
        trades = Trade.objects.filter(account=account).order_by('-date')
    except:
        raise Http404("No such account")


    data = serializers.serialize('json', trades)
    return HttpResponse(data, content_type='application/json')


@login_required
def render_personal_dashboard(request):
    context = {}

    try:
        account = get_object_or_404(Account, owner=request.user)
    except:
        raise Http404("No such user")

    try:
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        account_asset = TotalAsset.objects.filter(date=yesterday, account=account)[0]
        rank = TotalAsset.objects.filter(date=yesterday).filter(total_asset__gte=account_asset.total_asset).count()
        context['rank'] = '#' + str(rank)
    except IndexError:
        context['rank'] = 'NA'

    try:
        holds = Hold.objects.filter(account=account)
    except:
        raise Http404("No such account")
    stock_count = 0
    if not holds:
        context['stock_count'] = stock_count
    else:
        stock_count = holds.count()
    cost_list = []

    context['holds'] = holds
    context['stock_count'] = stock_count
    context['username'] = account.owner.username
    context['buying_power'] = account.buying_power

    return render(request, 'personal/dashboard_new.html', context)

@ login_required
def get_trend(request):
    context={}
    dates = []
    assets = []
    try:
        account = get_object_or_404(Account, owner=request.user)
    except:
        raise Http404("No such user")
    today = timezone.now().date()
    TotalAsset.fill_the_gap(account, today)
    totalAssets = TotalAsset.objects.filter(account=account).order_by('date')
    for totalAsset in totalAssets:
        dates.append(str(totalAsset.date))
        assets.append(float(totalAsset.total_asset))
    context['dates'] = dates
    context['assets'] = assets
    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')

def getTransactionsByDate(request, date):
    try:
        date_array = date.split("/")

        try:
            account = get_object_or_404(Account, owner=request.user)
        except:
            raise Http404("No such user")
        try:
            print (date_array[1])
            trades = Trade.objects.filter(account=account,
                                          # date__day__gte='01',
                                          date__day=date_array[1],
                                          date__year=date_array[2], date__month=date_array[0]
                                          )
        except:
            raise Http404("No such account")
        print ('----')
        for trade in trades:
            print (type(trade.date.day))
        data = serializers.serialize('json', trades)
        return HttpResponse(data, content_type='application/json')

    except:
        return redirect('personal_home')

def cal_prev_day(year, month, day):
    month_List_31 = [1, 3, 5, 7, 8, 10, 12]
    month_List_30 = [4, 6, 9, 11]
    if (int(day) - 1 <= 0):
        new_month = str(int(month) - 1)
        if (int(month) - 1 in month_List_31):
            new_day = '31'
        elif (int(month) - 1 in month_List_30):
            new_day = '30'
        else:
            new_day = '28'
    else:
        new_month = str(month)
        if (day < 10):
            new_day = '0'+str(int(day) - 1)
        else:
            new_day = str(int(day) - 1)

    res = str(year)+'-'+new_month + '-' + new_day
    return res