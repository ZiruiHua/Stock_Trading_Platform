"""
Script file used to bulk import Stock records to the database.

Run `python manage.py shell`, then run `exec(open("insert_stocks.py").read())`.

Author: Stephen Xie
"""
from MockInternetTraderSite.settings import *
from global_resources.models import Stock

import csv

"""
Function to bulk import Stock records from csv files.

Author: Jia Zheng
"""


def import_stocks():
    # url of csv file containing list of all companies
    file_url = os.path.join(BASE_DIR, 'search', 'static', 'csv', 'companylist_nasdaq.csv')
    with open(file_url) as f:
        reader = csv.reader(f)
        for counter, row in enumerate(reader):
            if counter > 0 and not Stock.objects.filter(symbol=row[0]):
                new_stock = Stock(symbol=row[0], name=row[1], company_description=row[6])
                new_stock.save()
                # TODO: amend Stock model to include more information
                # TODO: change get_stock_list method in search to use the database

#Stock(symbol='MSFT', name='Microsoft', company_description='A Software Company').save()
#Stock(symbol='GOOGL', name='Google', company_description='An Internet Company').save()
#Stock(symbol='AAPL', name='Apple', company_description='A Hardware Company').save()
#Stock(symbol='AMZN', name='Amazon', company_description='A Hybrid Company').save()
# TODO: call import_stocks
import_stocks()




