
from django.shortcuts import render, redirect
from django.urls import reverse
from apis.news_api import get_headlines



def home(request):
    if request.user.is_anonymous():
        errors = []
        articles = get_headlines(errors)
        context = {'articles': articles, 'errors': errors}
        return render(request, 'global/home.html', context)
    else:
        return redirect(reverse('global'))

