__author__ = 'marshynov'

from django.dispatch import Signal
from custom_auth.openam_backend_bridge import rest_interface
from openam_backend_bridge import SSOUser

user_login_failed = Signal(providing_args=['credentials'])
user_logged_in = Signal(providing_args=['request', 'user'])
ssouser_logged_in = Signal(providing_args=['request', 'ssouser'])
user_logged_out = Signal(providing_args=['request', 'user'])

OPEN_AM_SERVER_URL = 'http://localhost:8080/openam_10.0.1/'

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
REDIRECT_FIELD_NAME = 'next'
OPENAM_COOKIE_NAME_FOR_TOKEN = 'djnago_sso_secondday_token_id'


def auth_login(request, user):
    """
    is taken from       django.contrib.auth.__init__.py

    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """

    ri = rest_interface(opensso_url=OPEN_AM_SERVER_URL)

    token_logged_in = ri.do_login(request.REQUEST.get('username'),request.REQUEST.get('password'))

    if (ri.isErrorable(token_logged_in)):
        if request.COOKIES.has_key(OPENAM_COOKIE_NAME_FOR_TOKEN):
            del request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN]
        return None

    token_logged_in = ri.clear_token(token_logged_in)

    """
    if user is None:
        user = request.user
        # TODO: It would be nice to support different login methods, like signed cookies.
    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.pk:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    """

    #ssouser = SSOUser(True)


    ###########ssouser_logged_in.send(sender=ssouser.__class__, request=request, ssouser=ssouser)
    #request.session['somekey'] = 'test'

    """
    request.ssouser = ssouser
    if request.COOKIES.has_key(OPENAM_COOKIE_NAME_FOR_TOKEN):
        del request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN]
    request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN] = token_logged_in
    """

    #ri.save_token()

    return token_logged_in


def auth_logout(request):
    """
    is taken from       django.contrib.auth..__init__.py

    Removes the authenticated user's ID from the request and flushes their
    session data.
    """

    """
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)
    """
    request.session.flush()
    """
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    """
    ri = rest_interface(opensso_url=OPEN_AM_SERVER_URL)

    if OPENAM_COOKIE_NAME_FOR_TOKEN in request.COOKIES:
        unsigned_token = request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN]
        print('logout: token ='+request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN])
        print('logout: unsigned_token ='+unsigned_token)
        ri.do_logout(subject_id=unsigned_token)
        #del request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN]
        #request.COOKIES[OPENAM_COOKIE_NAME_FOR_TOKEN] = 'logged_out'
    ##ssouser = SSOUser(False)
    ##request.ssouser = ssouser