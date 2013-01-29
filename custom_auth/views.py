__author__ = 'marshynov'

from django.http import HttpResponseRedirect

#from django.shortcuts import resolve_url
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from custom_auth import REDIRECT_FIELD_NAME, auth_login, auth_logout
from django.template.response import TemplateResponse
from django.contrib.sites.models import get_current_site
from django.utils.http import base36_to_int, is_safe_url
from custom_auth.openam_backend_bridge import rest_interface
from django.core import urlresolvers
from . import OPEN_AM_SERVER_URL
from openam_backend_bridge import SSOUser
import custom_auth
from django_sso_secondday.settings import LOGIN_REDIRECT_TEMPLATE
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """

    is taken from       django.contrib.auth.views.py


    Displays the login form and handles the login action.

    """

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        print('form.is_valid()=='+str(form.is_valid()))
        ####if form.is_valid():
        ###token_to_store_in_cookies = auth_login(request, form.get_user())



        token_to_store_in_cookies = auth_login(request, form.get_user())
        if token_to_store_in_cookies:
            print('is_safe_url(url=redirect_to, host=request.get_host())='+str(is_safe_url(url=redirect_to, host=request.get_host())))
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
                #print('!!!!!!!!!! USER  '*20)

            #return HttpResponseRedirect('/mainmenu_POST/')
            print('logn===='+redirect_to+'======login')
            response = HttpResponseRedirect(redirect_to)
            print('token_to_store_in_cookies='+token_to_store_in_cookies)

            response.set_cookie(custom_auth.OPENAM_COOKIE_NAME_FOR_TOKEN, token_to_store_in_cookies)



            res = read_token_from_cookie_check_fill_out_ssouser_response(token_to_store_in_cookies,response)
            return response
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    # place to check 'djnago_sso_secondday_token_id' and set 'ssouser' in case of need
    # request.ssouser = SSOUser(True)

    can_be_redirected = read_token_from_cookie_then_check_and_fill_out_ssouser_object(request)
    """
        if can_be_redirected and bool(can_be_redirected):
            if redirect_to or len(redirect_to) > 0:
            #    redirect_to = LOGIN_REDIRECT_TEMPLATE
                return HttpResponseRedirect(redirect_to)
            #template_name = 'mainmenu.html'
    """

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        }

    #if extra_context is not None:
    #    context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)

def remove_token_from_cookies(request):
    del request.COOKIES[custom_auth.OPENAM_COOKIE_NAME_FOR_TOKEN]

def read_token_from_cookie_then_check_and_fill_out_ssouser_object(request):
    token = request.COOKIES.get(custom_auth.OPENAM_COOKIE_NAME_FOR_TOKEN, None)
    ri = rest_interface(opensso_url=OPEN_AM_SERVER_URL)
    authorized = ri.is_token_valid(token)
    request.ssouser =  SSOUser(authorized)
    #if not bool(authorized):
    #    remove_token_from_cookies(request)
    return authorized

def read_token_from_cookie_check_fill_out_ssouser_response(token, response):
    ri = rest_interface(opensso_url=OPEN_AM_SERVER_URL)
    authorized = ri.is_token_valid(token)
    response.ssouser = SSOUser(authorized)
    return authorized

def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    is taken from       django.contrib.auth.views.py


    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': 'Logged out'
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)

def resolve_url(to, *args, **kwargs):
    """

    is taken from           django.shortcuts.__init__.py


    Return a URL appropriate for the arguments passed.

    The arguments could be:

        * A model: the model's `get_absolute_url()` function will be called.

        * A view name, possibly with arguments: `urlresolvers.reverse()` will
          be used to reverse-resolve the name.

        * A URL, which will be returned as-is.

    """
    # If it's a model, use get_absolute_url()

    if hasattr(to, 'get_absolute_url'):
        return to.get_absolute_url()

    # Next try a reverse URL resolution.
    try:
        return urlresolvers.reverse(to, args=args, kwargs=kwargs)
    except urlresolvers.NoReverseMatch:
        # If this is a callable, re-raise.
        if callable(to):
            raise
            # If this doesn't "feel" like a URL, re-raise.
        if '/' not in to and '.' not in to:
            raise

    # Finally, fall back and assume it's a URL
    return to