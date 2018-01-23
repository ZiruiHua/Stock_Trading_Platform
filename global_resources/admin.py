from global_resources.models import *
from django.contrib import admin

# Register your models here.
admin.site.register(Stock)
admin.site.register(Account)
admin.site.register(Hold)
admin.site.register(Trade)
admin.site.register(TotalAsset)
admin.site.register(HoldingHistory)
admin.site.register(StockHistory)
admin.site.register(BuyingPowerHistory)