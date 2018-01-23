from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from global_resources.models import Account
from user_auth.forms import *


# TODO: parse all return values to JSON for React?
def register(request):
    if request.user.is_anonymous():
        status = []
        if request.method == 'GET':
            register_form = RegisterForm()
        if request.method == 'POST':
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                # save user
                new_user = register_form.save(commit=False)
                new_user.is_active = False
                new_user.save()
                # send verification email
                curr_site = get_current_site(request)
                message = render_to_string('user_auth/activate.html', {
                    'user': new_user,
                    'domain': curr_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                    'token': default_token_generator.make_token(new_user),
                })
                mail_subject = 'Activate your MIT account'
                to_email = register_form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                # add activation notification
                status.append('An email has been sent with intructions to activate your account.')
        return render(request, 'user_auth/register.html', {'form': register_form, 'status': status})
    else:
        redirect('/')  # TODO: redirect to user homepage


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        activate_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        activate_user = None
    if activate_user is not None and default_token_generator.check_token(activate_user, token):
        activate_user.is_active = True
        activate_user.save()
        # create new account and gives initial funds
        new_account = Account(owner=activate_user, buying_power=100000, initial_asset=100000)
        new_account.save()
        login(request, activate_user)
        return redirect('/')  # TODO: redirect to user homepage
    else:
        return HttpResponse('Activation link invalid.')
