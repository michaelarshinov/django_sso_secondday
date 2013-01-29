__author__ = 'marshynov'
from restclient import GET, POST
from django.conf import settings

import datetime
CMD_REST_LOGGING = 'identity/log'
CMD_REST_LOGOUT = 'identity/logout'
CMD_IS_TOKEN_VALID = 'identity/isTokenValid'
CMD_AUTHORIZATION = 'identity/authorize'
CMD_AUTHENTICATE = 'identity/authenticate'
CMD_ATTRIBUTES = 'identity/attributes'
CMD_ATTRIBUTE_RETRIEVAL = 'identity/read'
class rest_interface:
    """
    Use OpenAM RESTful Services:
        https://wikis.forgerock.org/confluence/display/openam/Use+OpenAM+RESTful+Services

    Inspired By:
        http://nielsbusch.dk/a-case-of-using-opensso-single-sign-on-with-d

    The OpenSSO REST Interfaces in Black / White
        https://blogs.oracle.com/docteger/entry/opensso_and_rest
    """
    opensso_url = ''

    def __init__(self, opensso_url='',):
        if not opensso_url:
            raise AttributeError('This interface needs an OpenSSO url to work!')
        self.opensso_url = opensso_url

    def _do_get(self, cmd, arguments):
        data = GET(''.join((self.opensso_url, cmd)), arguments)
        return data

    def do_login(self, username, password):
        #print(username + ',' + password+','+ self._do_get(CMD_AUTHENTICATE, {'username':username, 'password':password}))
        return self._do_get(CMD_AUTHENTICATE, {'username':username, 'password':password})

    def do_logout(self, subject_id):
        return self._do_get(CMD_REST_LOGOUT, {'subjectid':subject_id})

    def do_logging(self, app_id, subject_id, log_name, message):
        return self._do_get(CMD_REST_LOGGING, {
        'appid':app_id,
        'subjectid':subject_id,
        'logname':log_name,
        'message':message
        })

    def do_authorization(self, uri, action, subject_id):
        return self._do_get(CMD_AUTHORIZATION, {
            'uri': uri,
            'action': action,
            'subjectid': subject_id
        })

    def retrieve_attributes(self, subject_id):
        return self._do_get(CMD_ATTRIBUTES, {'subjectid': subject_id})

    def is_token_valid(self, token_id):
        is_valid = False
        try:
            is_valid = 'boolean=true' in self._do_get(CMD_IS_TOKEN_VALID, {'tokenid':token_id})
        except:
            pass
        return is_valid

    def do_authorization(self,uri, action, subject_id):
        return self._do_get(CMD_AUTHORIZATION, {'uri':uri, 'action':action, 'subjectid':subject_id})

    def get_attribute(self, name,
                     attributes_names,
                     attributes_values_realm,
                     admin):
        return self._do_get(CMD_ATTRIBUTE_RETRIEVAL, {
                'name':name,
                'attributes_names':attributes_names,
                'attributes_values_realm':attributes_values_realm,
                'admin': admin})


    def clear_token(self, token):
        #token.id=AQIC5wM2LY4SfczJxzJw4cc9guxWRo_JoQkinB30OzX_PjQ.*AAJTSQACMDE.*\n'
        try:
            cleared_token = token['token.id='.__len__():-1]
            return cleared_token
        except:
            return None #data.index('exception.name=')

    def isErrorable(self, data):
        try:
            data.index('exception.name')
            return True
        except:
            return False


class SSOUser:
    logged_in = False
    is_authenticated = True
    def __init__(self, logged_in):
        self.logged_in = logged_in

    def is_authenticated(self):
        return self.logged_in