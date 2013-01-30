__author__ = 'marshynov'
from django.contrib.auth import REDIRECT_FIELD_NAME
try:
    from urllib.parse import urlparse
except ImportError: # Python 2
    from urlparse import urlparse
from functools import wraps
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs

import codecs
import datetime
from decimal import Decimal
import locale
try:
    from urllib.parse import quote
except ImportError: # Python 2
    from urllib import quote
import warnings

from django.utils.functional import Promise
from django.utils import six

from django.core import urlresolvers

def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
Decorator for views that checks that the user passes the given test,
redirecting to the log-in page if necessary. The test should be a callable
that takes the user object and returns True if the user passes.
"""

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # urlparse chokes on lazy objects in Python 3, force to str
            resolved_login_url = force_str(
                resolve_url(login_url or settings.LOGIN_URL))
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def sso_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.

    reworked https://github.com/django/django/blob/master/django/contrib/auth/decorators.py

    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(perm, login_url=None, raise_exception=False):
    """
Decorator for views that checks whether a user has a particular permission
enabled, redirecting to the log-in page if neccesary.
If the raise_exception parameter is given the PermissionDenied exception
is raised.
"""
    def check_perms(user):
        # First check if the user has the permission (even anon users)
        if user.has_perm(perm):
            return True
            # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
            # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)


def resolve_url(to, *args, **kwargs):
    """
Return a URL appropriate for the arguments passed.

The arguments could be:

* A model: the model's `get_absolute_url()` function will be called.

* A view name, possibly with arguments: `urlresolvers.reverse()` will
be used to reverse-resolve the name.

* A URL, which will be returned as-is.

 reworked   https://github.com/django/django/blob/master/django/shortcuts/__init__.py
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

################   https://github.com/django/django/blob/master/django/utils/encoding.py <<<<<<<<<<<<<<


class DjangoUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (original, self.obj,
                                              type(self.obj))

def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

Objects of protected types are preserved as-is when passed to
force_text(strings_only=True).
"""
    return isinstance(obj, six.integer_types + (type(None), float, Decimal,
                                                datetime.datetime, datetime.date, datetime.time))


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
Similar to smart_text, except that lazy instances are resolved to
strings, rather than kept as lazy objects.

If strings_only is True, don't convert (some) non-string-like objects.
"""
    # Handle the common case first, saves 30-40% when s is an instance of
    # six.text_type. This function gets called often in that setting.
    if isinstance(s, six.text_type):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not isinstance(s, six.string_types):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                if six.PY3:
                    if isinstance(s, bytes):
                        s = six.text_type(s, encoding, errors)
                    else:
                        s = six.text_type(s)
                else:
                    s = six.text_type(bytes(s), encoding, errors)
        else:
            # Note: We use .decode() here, instead of six.text_type(s, encoding,
            # errors), so that if s is a SafeBytes, it ends up being a
            # SafeText at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise DjangoUnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join([force_text(arg, encoding, strings_only,
                errors) for arg in s])
    return s

#if six.PY3:
#    smart_str = smart_text
force_str = force_text
#else:
#    smart_str = smart_bytess
#    force_str = force_bytes
    # backwards compatibility for Python 2
#    smart_unicode = smart_text
#    force_unicode = force_text

################   https://github.com/django/django/blob/master/django/utils/encoding.py >>>>>>>>>>>>>>