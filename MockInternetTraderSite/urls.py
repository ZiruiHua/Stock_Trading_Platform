"""MockInternetTraderSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

import global_resources.views


urlpatterns = [
    url(r'^$', global_resources.views.home, name='home'),
    url(r'^global/', include('global_dashboard.urls')),
    url(r'^auth/', include('user_auth.urls')),
    url(r'^personal/', include('personal_dashboard.urls')),
    url(r'^stock/', include('stock_view.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^data-api/', include('apis.urls')),
    url(r'^admin/', admin.site.urls)
]

# allows media urls in template; this should not be necessary if context processor
# 'django.template.context_processors.media' is working in settings.py
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
