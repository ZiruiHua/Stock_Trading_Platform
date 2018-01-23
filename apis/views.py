"""
A mask of the Alpha Vantage API service:
https://www.alphavantage.co/documentation/

"""
from django.http import HttpResponse, HttpResponseBadRequest, Http404

from global_resources.exceptions import Http400Error, Http404Error
from .alpha_vantage_api import get_current_price

# NOTE: don't leak the API key to the wild!!!
api_base_url = 'https://www.alphavantage.co/query?function={0}&symbol={1}&apikey=7OKTKQYQQ2SW1ZO5'


# @login_required
def query_current_price(request, stock_symbol=''):
    """
    Get the latest price of a specified stock.

    :param request:
    :param stock_symbol: stock symbol
    :return: a single float number indicating the price, or an error message
    """
    try:
        price = get_current_price(stock_symbol)
    except Http400Error as err:
        return HttpResponseBadRequest(err.message)
    except Http404Error as err:
        return Http404(err.message)

    return HttpResponse(price) 