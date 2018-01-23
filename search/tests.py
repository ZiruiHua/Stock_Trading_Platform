from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.test import TestCase

from global_resources.models import *
from search.views import *

import json

class SearchTests(TestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='testpwd')
        self.client.login(username='testuser', password='testpwd')
        # Create stock entries
        Stock(symbol='MSFT', name='Microsoft', company_description='Computer software: prepackaged software').save()
        Stock(symbol='GOOGL', name='Google', company_description='Computer software: programming, data processing').save()
        Stock(symbol='AAPL', name='Apple', company_description='Computer manufacturing').save()
        Stock(symbol='AMZN', name='Amazon', company_description='Catalog/specialty distribution').save()

    def testUrlExistsAndReqSuccessful(self):
        res = self.client.get('/search/')
        self.assertEqual(res.status_code, 200)
    
    def testReverseExistsAndReqSuccessful(self):
        res = self.client.get(reverse('search'))
        self.assertEqual(res.status_code, 200)

    def testLoadStockList(self):
        res = self.client.get(reverse('list', kwargs={'page': 0}))
        self.assertEqual(res.status_code, 200)
        json_output = json.loads(res.content)
        self.assertEqual(len(json_output['stocks']), 4)

    def testSearchEngine(self):
        res = self.client.get(reverse('query'), {'query': 'google'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('google', str(res.content))



