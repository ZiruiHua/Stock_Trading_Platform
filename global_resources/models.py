import json
import logging

from channels import Group
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from apis.alpha_vantage_api import get_stock_price


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    company_description = models.CharField(max_length=500)

    def __unicode__(self):
        return self.name


class Account(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account',
        primary_key=True
    )
    # how much money does this user have?
    buying_power = models.DecimalField(decimal_places=2, max_digits=10)
    # how much money does this user initially have?
    initial_asset = models.DecimalField(decimal_places=2, max_digits=10)
    # stocks user subscribed to
    watched_stocks = models.ManyToManyField(Stock)

    def __unicode__(self):
        return self.owner_id

    # override the save method so that the BuyingPowerHistory model will also
    # be updated every time the buying_power field is updated
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        today = timezone.now().date()
        buying_power_now = BuyingPowerHistory.objects.filter(account=self, date=today)
        if buying_power_now.exists():
            # we already have an record for today in BuyingPowerHistory;
            # just update the existing record
            buying_power_now = buying_power_now[0]
            buying_power_now.remaining_money = self.buying_power
            buying_power_now.save()
        else:
            # create a new record
            BuyingPowerHistory.objects.create(
                account=self,
                remaining_money=self.buying_power
            ).save()


class Hold(models.Model):
    """
    This records the amount of a specified stock a given user currently holds.
    """
    shares = models.IntegerField()  # shares of a stock that account holds now
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    average_cost = models.DecimalField(decimal_places=2, max_digits=6, default='0.00')

    def __unicode__(self):
        return self.shares


class Trade(models.Model):
    """
    This records each transaction made site-wide.
    """
    type = models.BooleanField()  # true means buy-in, false means sell-out
    price = models.DecimalField(decimal_places=2, max_digits=6)
    shares = models.IntegerField()  # shares of a stock in this transaction
    date = models.DateTimeField(default=timezone.now)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.account_id

    @property
    def html(self):
        op = 'Buy' if self.type else 'Sell'
        return """
        <td>{0}</td>
        <td>{1}</td>
        <td>{2}</td>
        <td>{3}</td>
        <td>{4}</td>
        <td>{5}</td>
        """.strip().format(self.account.owner.username, self.stock.symbol, op,
                           self.shares, self.price, self.date.strftime('%d %b %Y %H:%M%p'))

    # override the save method to send real-time trade messages
    # to the trade_stream group
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # send the trade record to the group; all consumers (aka "listeners") to that group
        # will be notified
        # WebSocket text frame, with JSON content
        Group('trade_stream').send({
            'text': json.dumps({
                'id': self.id,
                'html': self.html
            })
        })


class TotalAsset(models.Model):
    """
    This records the final total asset value (according to the closing prices) of each user every day;
    only records till yesterday. Notice that due to the limitation of Django's synchronous nature, you
    *MUST* call fill_the_gap(account, date) before retrieving any information in this model.

    This model is made to minify the amount of price query requests to the external stock info API,
    as it's quite slow. We'll only calculate total asset worth till yesterday using closing prices,
    therefore for each day we only need to query price of each stock at most once regarding total asset
    queries.
    """
    date = models.DateField(default=timezone.now().date())
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    total_asset = models.DecimalField(decimal_places=2, max_digits=15)

    def __unicode__(self):
        return self.account_id

    @staticmethod
    def fill_the_gap(account, date):
        """
        Update the table to include continuous records up until the day before the given date.

        :param account:
        :param date:
        :return:
        """
        try:
            last_record = TotalAsset.objects.filter(account=account).order_by('-date')[0]
            inc = timezone.timedelta(days=1)  # days are incremented / decremented by 1 at a time
            yesterday = date - inc

            if last_record.date < yesterday:
                # we don't have a record yesterday (or possibly more records missing); calculate now
                BuyingPowerHistory.fill_the_gap(account=account, date=date)  # fill any potential gaps up till yesterday
                for day in date_range(last_record.date + inc, date):
                    holdings = HoldingHistory.objects.filter(account=account, date=day)
                    try:
                        total_money = BuyingPowerHistory.objects.filter(account=account, date=day)[0].remaining_money
                        total_stocks_worth = 0
                        for hold in holdings:
                            try:
                                # TODO: right now this issues potentially duplicate calls to external API
                                # to get a list of historical prices
                                day_price = get_stock_price(hold.stock.symbol, date_str=date.strftime('%Y-%m-%d')) # YYYY-MM-DD
                                total_stocks_worth += day_price * hold.shares
                            except IndexError:
                                # TODO: due to the limitation of the external data API (either get the last 20 days of
                                # data or get the last 20 years of data in one query), for performance concerns this
                                # method doesn't work for getting history later than 20 days ago; we may cache the
                                # results of 20 in database to work around this limitation in the future
                                logger.error("ERROR: Cannot get yesterday price for stock " + hold.stock.symbol)

                        total_asset = total_money + total_stocks_worth
                        # create a new record in the database
                        TotalAsset.objects.create(date=day, account=account, total_asset=total_asset).save()

                        return total_asset
                    except IndexError:
                        logger.error("ERROR: Total buying power history is not found for day " + day)

        except IndexError:
            # there's no record in the model regarding the current user
            return

    @staticmethod
    def get_yesterday_total(account):
        """
        Get the total asset worth of the given account yesterday.

        :param account:
        :return:
        """
        # fill any potential gaps until yesterday
        today = timezone.now().date()
        TotalAsset.fill_the_gap(account=account, date=today)

        yesterday = today - timezone.timedelta(days=1)
        try:
            return TotalAsset.objects.filter(account=account, date=yesterday)[0].total_asset
        except IndexError:
            logger.error("ERROR: total asset record for yesterday not found.")


class BuyingPowerHistory(models.Model):
    """
    This records the final remaining buying power (money) a given user had every day;
    for today, this will mean the latest buying power. Notice that due to the limitation
    of Django's synchronous nature, you *MUST* call fill_the_gap(account, date) before
    retrieving any information in this model.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().date())
    remaining_money = models.DecimalField(decimal_places=2, max_digits=10)

    # override the save method to fill any potential record gap
    # in the database
    def save(self, *args, **kwargs):
        self.fill_the_gap(self.account, self.date)

        super().save(*args, **kwargs)

    @staticmethod
    def fill_the_gap(account, date):
        """
        Update the table to include continuous records up until the day before the given date.
        :param account:
        :param date:
        :return:
        """
        try:
            last_record = BuyingPowerHistory.objects.order_by('-date')[0]

            if (date - last_record.date).days > 1:
                # the previous records are not complete; fill the gap now
                inc = timezone.timedelta(days=1)  # days are incremented / decremented by 1 at a time
                for day in date_range(last_record.date + inc, date):
                    # copy the last_record up until the day before yesterday
                    BuyingPowerHistory.objects.create(
                        account=account,
                        date=day,
                        remaining_money=last_record.remaining_money
                    ).save()
        except IndexError:
            # the model is still empty
            return


class HoldingHistory(models.Model):
    """
    This records the amount of a specified stock the given user FINALLY holds every day;
    for today, this will mean the latest holding info.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().date())
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.IntegerField()

    def __unicode__(self):
        return self.pk

    """
    This static method fills gap of HoldingHistory when the previous record is
    not present in the database.
    """
    @staticmethod
    def fill_the_gap(account, date):
        try:
            # Get list of stock in records
            stock_list_val = HoldingHistory.objects.filter(account=account).values('stock').distinct()
            # For each stock that was previously traded
            for s in stock_list_val:
                stock_obj = Stock.objects.filter(symbol=s['stock'])[0]
                # Get last trade record of the stock and date
                last_record = HoldingHistory.objects.filter(account=account).filter(stock=stock_obj).latest('date')
                last_record_date = last_record.date.date()
                inc = timezone.timedelta(days=1)
                # for each record date
                for day in date_range(last_record_date + inc, date):
                    # copy the last_record up until the day before yesterday
                    HoldingHistory.objects.create(
                        account=account,
                        date=day,
                        stock=last_record.stock,
                        shares=last_record.shares
                    ).save()
        except:
            # no record found associated with this user
            return


class StockHistory(models.Model):
    """
    A simple model for caching stock data from the external stock info API.
    """
    symbol = models.CharField(max_length=10, default="default")
    price = models.DecimalField(decimal_places=2, max_digits=6)
    date = models.CharField(max_length=20)  # yyyy-mm-dd


# --- Helper functions -----------------------------

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
