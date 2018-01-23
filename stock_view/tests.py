from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.test import TestCase

from global_resources.models import *
from stock_view.views import *

class StockTests(TestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='testpwd')
        # TODO: Fix setup, user_account is null right now
        self.user_account = Account(owner=self.user, buying_power=10000.00, initial_asset=10000.00).save()
        self.client.login(username='testuser', password='testpwd')
        # Create stock entries
        self.microsoft = Stock(symbol='MSFT', name='Microsoft', company_description='Computer software: prepackaged software').save()
        self.google = Stock(symbol='GOOGL', name='Google', company_description='Computer software: programming, data processing').save()
        self.apple = Stock(symbol='AAPL', name='Apple', company_description='Computer manufacturing').save()
        self.amazon = Stock(symbol='AMZN', name='Amazon', company_description='Catalog/specialty distribution').save()
        # Create hold entry for selling
        Hold(shares=5, stock=self.amazon, account=self.user_account).save()
        # Add AMZN to watched list
        self.user_account.watched_stocks.add(self.amazon)

    def testUrlExistsAndReqSuccessful(self):
        res = self.client.get('/stock/MSFT')
        self.assertEqual(res.status_code, 200)

    def testReverseExistsAndReqSuccessful(self):
        res = self.client.get(reverse('stock_view', kwargs={'stock_symbol': 'GOOG'}))
        self.assertEqual(res.status_code, 200)

    def testBuyStockHoldIncreases(self):
        buy_stock = Stock.objects.get(symbol='AAPL')
        try:
            old_hold = Hold.objects.get(stock=buy_stock, account=self.user_account).shares
        except:
            old_hold = 0
        res = self.client.post('/stock/buy', {'stock_symbol': 'AAPL', 'amount': '1'})       
        if res.status_code == 200:
            try:
                new_hold = Hold.objects.get(stock=buy_stock, account=self.user_account).shares
            except:
                new_hold = 0
            assertEqual(old_hold + 1, new_hold)

    def testSellStockHoldDecreases(self):
        sell_stock = Stock.objects.get(symbol='AMZN')
        try:
            old_hold = Hold.objects.get(stock=sell_stock, account=self.user_account).shares
            res = self.client.post('/stock/sell', {'stock_symbol': 'AMZN', 'amount': '1'})
            if res.status_code == 200:
                try:
                    new_hold = Hold.objects.get(stock=sell_stock, account=self.user_account).shares
                except:
                    new_hold = 0
                assertEqual(old_hold - 1, new_hold)
        except:
            old_hold = 0

    def testBuyStockBuyingPowerDecreases(self):
        old_bp = self.user_account.buying_power
        res = self.client.post('/stock/buy', {'stock_symbol': 'AAPL', 'amount': '1'})       
        if res.status_code == 200:
            assertGreater(old_bp, self.user_account.buying_power)
        else:
            assertEqual(old_bp, self.user_account.buying_power)

    def testSellStockBuyingPowerIncreases(self):
        old_bp = self.user_account.buying_power
        res = self.client.post('/stock/sell', {'stock_symbol': 'AMZN', 'amount': '1'})
        if res.status_code == 200:
            assertLess(old_bp, self.user_account.buying_power)
        else:
            assertEqual(old_bp, self.user_account.buying_power)

    def watchStockAddToWatched(self):
        res = self.client.post('/stock/subscribe', {'symbol': 'MSFT'})
        if res.status_code == 200:
            assertIn(self.microsoft, self.user_account.watched_stocks)

    def unwatchStockRemovedFromWatched(self):
        res = self.client.post('/stock/unsubscribe', {'symbol': 'AMZN'})
        if res.status_code == 200:
            assertNotIn(self.amazon, self.user_account.watched_stocks)

