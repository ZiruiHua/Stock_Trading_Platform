import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseBadRequest, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404

from apis.alpha_vantage_api import get_current_price
from global_resources.exceptions import Http400Error, Http404Error
from global_resources.models import *
import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def stock_view(request, stock_symbol=''):
    if not stock_symbol:
        errors = []
        context = {'errors': errors}
        errors.append('Please specify a stock symbol.')
    else:
        context = {}
        context['stock_symbol'] = stock_symbol

        current_account = Account.objects.get(owner__exact=request.user)
        try:
            target_stock = Stock.objects.filter(symbol__exact=stock_symbol)[0]
            context['stock_name'] = target_stock.name
            if current_account.watched_stocks.filter(symbol=stock_symbol):
                context['stock_watched'] = 'Unwatch'
            else:
                context['stock_watched'] = 'Watch'
        except IndexError:
            return HttpResponseBadRequest('Stock is not on database.')

        try:
            # get the current price from the API
            price = get_current_price(stock_symbol)
        except Exception as err:
            return HttpResponseBadRequest(err.message)

        account_deposit = float(current_account.buying_power)
        context['buying_power'] = account_deposit

        try:
            context['available_shares'] = int(account_deposit / float(price))
        except TypeError:
            context['available_shares'] = 'NA'

        existing_stock_hold = Hold.objects.filter(account=current_account, stock=target_stock)
        if existing_stock_hold.exists():
            existing_stock_hold = existing_stock_hold.first()
            current_share = existing_stock_hold.shares
            context['current_share'] = current_share
        else:
            context['current_share'] = '0'

    return render(request, 'stock_view/stock.html', context)


@login_required
@transaction.atomic
def buy_stock(request):
    current_user = request.user

    if 'amount' in request.POST and request.POST['amount'] \
            and 'stock_symbol' in request.POST and request.POST['stock_symbol']:

        current_account = Account.objects.get(owner__exact=current_user)

        try:
            amount = int(request.POST['amount'])
        except ValueError:
            logger.error('Buy amount must be an integer.')
            return HttpResponseBadRequest('Buy amount must be an integer.')
        try:
            stock_symbol = request.POST['stock_symbol'].upper()
        except:
            logger.error('Invalid stock symbol.')
            return HttpResponseBadRequest('Invalid stock symbol.')

        # -- first check if that stock is on record ---------------------

        try:
            target_stock = Stock.objects.get(symbol__exact=stock_symbol)
        except Stock.DoesNotExist:
            logger.error('Stock is not on database.')
            return HttpResponseBadRequest('Stock is not on database.')

        # -- then calculate value of the stocks -------------------

        try:
            # get the current price from the API
            price = get_current_price(stock_symbol)
        except Http400Error as err:
            logger.error('400: ' + err.message)
            return HttpResponseBadRequest(err.message)
        except Http404Error as err:
            logger.error('404: ' + err.message)
            return Http404(err.message)

        total_value = price * amount

        # -- then check if the user has enough money ---------------------------

        account_deposit = float(current_account.buying_power)
        if total_value > account_deposit:
            logger.error('User doesn\'t have enough money.')
            return HttpResponseBadRequest('User doesn\'t have enough money.')
        else:
            # -- the transaction is legit; do it! --------------------------------------------------------
            account_deposit -= total_value
            # update account buying power
            current_account.buying_power = account_deposit
            current_account.save()
            # then create a new holding record / update the existing one
            existing_stock_hold = Hold.objects.filter(account=current_account, stock=target_stock)
            if existing_stock_hold.exists():
                existing_stock_hold = existing_stock_hold.first()
                # average cost is new total value / total shares
                average_cost = (total_value + existing_stock_hold.shares * float(existing_stock_hold.average_cost)) / (
                        existing_stock_hold.shares + amount)
                existing_stock_hold.average_cost = average_cost
                existing_stock_hold.shares += amount
                existing_stock_hold.save()
            else:
                # add average_cost filed
                new_stock_hold = Hold.objects.create(shares=amount, stock=target_stock, account=current_account,
                                                     average_cost=price)
                new_stock_hold.save()

            # finally, record this transaction
            new_trade = Trade(type=True, price=price, shares=amount, stock=target_stock, account=current_account)
            new_trade.save()



            # last update holding history
            # update holding history
            today = datetime.date.today()
            hs = HoldingHistory.objects.filter(account=current_account, stock=target_stock,
                                                             date__year=today.year, date__month=today.month,
                                                             date__day=today.day)
            # get latest shares
            existing_stock_hold = Hold.objects.filter(account=current_account, stock=target_stock).first()
            if hs.exists():
                print ("exist!!")
                holding_history = hs.first()
                # update share of holding history
                holding_history.shares = existing_stock_hold.shares
                holding_history.save()
            return HttpResponse()

    else:
        logger.error('Invalid HTTP methods or parameters.')
        return HttpResponseBadRequest('Invalid HTTP methods or parameters.')


@login_required
@transaction.atomic
def sell_stock(request):
    current_user = request.user

    if 'amount' in request.POST and request.POST['amount'] \
            and 'stock_symbol' in request.POST and request.POST['stock_symbol']:

        current_account = Account.objects.get(owner__exact=current_user)

        try:
            amount = int(request.POST['amount'])
        except ValueError:
            logger.error('Sell amount must be an integer.')
            return HttpResponseBadRequest('Sell amount must be an integer.')
        try:
            stock_symbol = request.POST['stock_symbol'].upper()
        except:
            logger.error('Invalid stock symbol.')
            return HttpResponseBadRequest('Invalid stock symbol.')

        # -- first check if the stock is on database & user has that many stocks --------------

        try:
            target_stock = Stock.objects.get(symbol__exact=stock_symbol)
        except Stock.DoesNotExist:
            logger.error('Stock is not on database.')
            return HttpResponseBadRequest('Stock is not on database.')

        try:
            stock_holdings = Hold.objects.get(account=current_account, stock=target_stock)
        except ObjectDoesNotExist:
            logger.error('User hasn\'t purchased this stock.')
            return HttpResponseBadRequest('User hasn\'t purchased this stock.')
        stock_holdings_count = stock_holdings.shares
        logger.error("Stock count: " + str(stock_holdings_count))
        if amount > stock_holdings_count:
            logger.error('User doesn\'t have enough stocks.')
            return HttpResponseBadRequest('User doesn\'t have enough stocks.')

        # -- then calculate value of the stocks -------------------

        try:
            # get the current price
            price = get_current_price(stock_symbol)
        except Http400Error as err:
            logger.error('400: ' + err.message)
            return HttpResponseBadRequest(err.message)
        except Http404Error as err:
            logger.error('404: ' + err.message)
            return Http404(err.message)
        total_value = price * amount

        # -- then do the transaction! ---------------------------
        account_deposit = float(current_account.buying_power)
        account_deposit += total_value

        # update account buying power
        current_account.buying_power = account_deposit
        current_account.save()
        # update the holding record
        stock_holdings.shares -= amount
        if stock_holdings.shares <= 0:
            # if user sold out his stock, delete entry
            stock_holdings.delete()
        else:
            # recalculate average cost
            average_cost = (stock_holdings.shares * float(stock_holdings.average_cost) - total_value) / (
            stock_holdings.shares - amount)
            stock_holdings.average_cost = average_cost
            stock_holdings.save()

        # finally, record this transaction
        new_trade = Trade(type=False, price=price, shares=amount, stock=target_stock, account=current_account)
        new_trade.save()

        # update holding history
        today = datetime.date.today()

        hs = HoldingHistory.objects.filter(account=current_account, stock=target_stock,
                                           date__year=today.year, date__month=today.month,
                                           date__day=today.day)
        # update share and price or insert
        existing_stock_hold = Hold.objects.filter(account=current_account, stock=target_stock).first()

        if hs:
            holding_history = hs.first()
            # update share of holding history
            holding_history.shares = existing_stock_hold.shares
            holding_history.save()
        return HttpResponse()

    else:
        logger.error('Invalid HTTP methods or parameters.')
        return HttpResponseBadRequest('Invalid HTTP methods or parameters.')


# Add stock to watched list
@login_required
def subscribe(request):
    if request.method == 'POST':
        if 'stock_symbol' in request.POST and request.POST['stock_symbol']:
            try:
                user_account = Account.objects.get(owner__exact=request.user)
                stock_symbol = request.POST['stock_symbol'].upper()
                to_subscribe = Stock.objects.get(symbol__exact=stock_symbol)
                user_account.watched_stocks.add(to_subscribe)
                return HttpResponse('Stock added to watched list.')
            except Exception as e:
                return Http404(e.message)
    return HttpResponseBadRequest('Invalid HTTP methods or parameters.')


# Remove stock to watched list
@login_required
def unsubscribe(request):
    if request.method == 'POST':
        if 'stock_symbol' in request.POST and request.POST['stock_symbol']:
            try:
                user_account = Account.objects.get(owner__exact=request.user)
                stock_symbol = request.POST['stock_symbol'].upper()
                to_unsubscribe = Stock.objects.get(symbol__exact=stock_symbol)
                if user_account.watched_stocks.filter(symbol=stock_symbol):
                    user_account.watched_stocks.remove(to_unsubscribe)
                return HttpResponse('Stock removed from watched list.')
            except Exception as e:
                return Http404(e.message)
    return HttpResponseBadRequest('Invalid HTTP methods or parameters.')


# Get buying power
@login_required
def buying_power(request):
    try:
        account = Account.objects.get(owner__exact=request.user)
        return HttpResponse(account.buying_power)
    except:
        raise Http404



