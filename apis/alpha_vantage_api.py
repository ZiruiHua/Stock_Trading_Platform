"""
Helper functions for making API calls to the Alpha Vantage service
inside Django views.

"""
import json
import random
import urllib

from django.utils import timezone

from global_resources.exceptions import Http400Error, Http404Error

# NOTE: don't leak the API key to the wild!!!
api_base_url = 'https://www.alphavantage.co/query?function={0}&symbol={1}&apikey=7OKTKQYQQ2SW1ZO5'


def get_current_price(stock_symbol):
    """
    Get the latest price of a given stock.

    :param stock_symbol: the stock symbol
    :return: a float number representing the latest price
    """
    if not stock_symbol:
        raise Http400Error('Please specify a stock symbol.')
    else:
        # read from Alpha Vantage API
        realtime_query = api_base_url.format('TIME_SERIES_INTRADAY', stock_symbol) + '&interval=1min'
        response = urllib.request.urlopen(realtime_query).read()
        # parse JSON response
        res_parsed = json.loads(response.decode('UTF-8'))

        if 'Error Message' in res_parsed:
            raise Http400Error('Invalid stock symbol.')
        else:
            try:
                last_refreshed_time = res_parsed['Meta Data']['3. Last Refreshed']
                price = float(res_parsed['Time Series (1min)'][last_refreshed_time]['4. close'])
            except:
                price = random.uniform(10.0, 500.0)  # fail safe in case API goes down
                # return Http404Error('API service is down.')

        return price


def get_historical_prices(stock_symbol, num):
    """
    Get a list of the historical prices of a given stock.

    :param stock_symbol: the stock symbol
    :param num: the amount of prices to be returned, sorted in reverse chronological order
    :return: a series of float numbers representing historical prices
    """
    if not stock_symbol:
        raise Http400Error('Please specify a stock symbol.')
    else:
        # read from Alpha Vantage API
        realtime_query = api_base_url.format('TIME_SERIES_DAILY', stock_symbol)
        response = urllib.request.urlopen(realtime_query).read()
        # parse JSON response
        res_parsed = json.loads(response.decode('UTF-8'))
        prices = {}
        if 'Error Message' in res_parsed:
            raise Http400Error('Invalid stock symbol.')
        else:
            try:
                record_dict = res_parsed['Time Series (Daily)']
                keys = list(dict.keys())
                # get the latest five days price data
                for i in range(num):
                    date = keys[i]
                    price = record_dict[date]['4. close']
                    prices[date] = price
            except:
                inc = timezone.timedelta(days=1)  # days are incremented / decremented by 1 at a time
                today = timezone.now().date()
                for day in date_range(today - num * inc, today + inc):
                    prices[day.strftime("%Y-%m-%d")] = random.uniform(10.0, 500.0)  # fail safe in case API goes down
                # return Http404Error('API service is down.')
        return prices


def get_stock_price(stock_symbol, date_str):
    """
    Get the closing price of a given stock at a specified date. Note that due to the API limitation, for performance
    concerns this method will not be able to retrieve data of date later than 20 days from today.

    :param stock_symbol:
    :param date_str: a date string in this format: 'YYYY-MM-DD'
    :return:
    """
    if not stock_symbol:
        raise Http400Error('Please specify a stock symbol.')
    else:
        # read from Alpha Vantage API
        realtime_query = api_base_url.format('TIME_SERIES_DAILY', stock_symbol)
        response = urllib.request.urlopen(realtime_query).read()
        # parse JSON response
        res_parsed = json.loads(response.decode('UTF-8'))
        if 'Error Message' in res_parsed:
            raise Http400Error('Invalid stock symbol.')
        else:
            try:
                record_dict = res_parsed['Time Series (Daily)']
                return float(record_dict[date_str]['4. close'])
            except:
                return random.uniform(10.0, 500.0)
                # return Http404Error('API service is down.')

def date_range(start_date, end_date):
    """
    A python generator for yielding a list of dates within a date range.

    :param start_date: starting date, inclusive
    :param end_date: ending date, exclusive
    :return:
    """
    inc = timezone.timedelta(days=1)  # days are incremented / decremented by 1 at a time
    day = start_date - inc
    while day < end_date:
        day += inc
        yield day
