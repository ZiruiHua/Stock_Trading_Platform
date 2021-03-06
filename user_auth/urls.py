from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('^register/$', views.register, name='register'),
    url('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    url(r'^login/$',
        auth_views.LoginView.as_view(template_name='user_auth/login.html'),
        name='login'),
    url(r'^logout/$',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'),
    url(r'^password_change/$',
        auth_views.PasswordChangeView.as_view(
            template_name='user_auth/password_change_form.html'
        ),
        name='password_change'),
    url(r'^password_change/done/$',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='user_auth/password_change_done.html'
        ),
        name='password_change_done'),
    url(r'^password_reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='user_auth/password_reset_form.html',
            email_template_name='user_auth/password_reset_email.html'
        ),
        name='password_reset'),
    url(r'^password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user_auth/password_reset_done.html'
        ),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user_auth/password_reset_confirm.html'
        ),
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user_auth/password_reset_complete.html'
        ),
        name='password_reset_complete'),
]
