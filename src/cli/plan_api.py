'''
Account and bearer token of this install on the Meile plan API.

The app used to call the plan API with one static username/password that was
compiled into the obfuscated client (PLANUSERNAME/PLANPASSWORD of scrtsxx.py),
so every install shared the same account and banning it would have locked out
the whole fleet.  Now every install asks /register for its own account once
(with the shared REGISTRATION_KEY of scrtsxx.py), keeps it in the [network]
section of config.ini as muser/mpassword and calls the API with a short lived
bearer token minted by /api/token (mtoken/mexpire, so a restart reuses the
token until it lapses).

The API accepts the token on every data endpoint while multi_auth is still in
place (see meile-plan-rest), so the token can be rolled out ahead of it: once
the shipped builds all use it, basic auth can be dropped from the API, and a
single account - or a single token - can be banned server side without
shipping a new app.
'''

from functools import partial
from threading import RLock
from time import time

from adapters import HTTPRequests
from conf.meile_config import MeileGuiConfig
from fiat.stripe_pay.dist import scrtsxx
from requests.auth import AuthBase, HTTPBasicAuth
from typedef.konstants import HTTParams, PlanAPI

# Marks a request that was already replayed with a fresh token, so a refused
# token can never cause a loop.
RETRY_HEADER = 'X-Meile-Token-Retry'


class BearerAuth(AuthBase):
    '''`requests` auth sending the bearer token of the plan API.

    A token can be refused before the expiry recorded in config.ini (the API
    was restarted with a new signing key, or the account was reset), so a 401
    mints a fresh token and replays the request once.  The API answers 401 in
    its authentication decorator, before the view runs, so a replay cannot
    repeat a side effect such as adding a subscription.
    '''

    def __init__(self, api):
        self.api = api

    def __call__(self, request):
        token = self.api.token()
        request.headers['Authorization'] = 'Bearer ' + token
        request.register_hook('response', partial(self._replay, token))
        return request

    def _replay(self, token, response, **kwargs):
        if response.status_code != 401:
            return response
        if response.request.headers.get(RETRY_HEADER):
            return response

        self.api.forget()
        try:
            fresh = self.api.token()
        except Exception as e:
            print('Meile API token renewal failed: %s' % str(e))
            return response
        if fresh == token:
            return response

        # Replay the request with the new token, the way requests' own digest
        # auth retries a 401.
        try:
            response.content        # drain, so the connection is reusable
            response.close()
            request = response.request.copy()
            request.headers['Authorization'] = 'Bearer ' + fresh
            request.headers[RETRY_HEADER] = '1'
            replayed = response.connection.send(request, **kwargs)
            replayed.history.append(response)
            replayed.request = request
            return replayed
        except Exception as e:
            print('Meile API token replay failed: %s' % str(e))
            return response


class MeilePlanAPI():
    '''Account and bearer token of this install (see the module docstring).

    Everything is a class method on purpose: the account and the token belong
    to the install, not to a screen, so the plan screen, the payment workers
    and the SMS screen all share one cache and one renewal.  The lock makes
    sure that two threads that need a token at the same time mint only one.
    '''

    _lock    = RLock()
    _token   = None     # in-memory copy of PlanAPI.TOKEN
    _expires = 0.0      # in-memory copy of PlanAPI.EXPIRES

    # --------------------------------------------------------------- account
    @classmethod
    def credentials(cls, force=False):
        '''(username, password) of this install, registering it when needed.

        The credentials are only asked for once: they are read from config.ini
        and a missing pair (a fresh install, or a config file that was reset)
        is registered with the plan API.
        '''
        with cls._lock:
            if not force:
                user, password = cls._stored_credentials()
                if user and password:
                    return user, password
            return cls._register()

    @classmethod
    def register(cls):
        '''Ask /register for a fresh account for this install and store it.'''
        with cls._lock:
            return cls._register()

    # ----------------------------------------------------------------- token
    @classmethod
    def token(cls, force=False):
        '''A bearer token that is valid for at least PlanAPI.SKEW seconds.'''
        with cls._lock:
            if not force:
                token = cls._cached_token()
                if token:
                    return token
            return cls._mint_token()

    @classmethod
    def forget(cls):
        '''Drop the cached token (it was refused, or the account changed).'''
        with cls._lock:
            cls._token = None
            cls._expires = 0.0
            cls._store_token('', 0)

    # ------------------------------------------------------------------ auth
    @classmethod
    def auth(cls):
        '''`requests` auth of a plan API call (see BearerAuth).'''
        return BearerAuth(cls)

    @classmethod
    def headers(cls):
        '''Headers of a plan API call, for the Kivy UrlRequest of the app.'''
        return {'Authorization': 'Bearer ' + cls.token()}

    # ------------------------------------------------------------- internals
    @staticmethod
    def _config():
        return MeileGuiConfig()

    @classmethod
    def _section(cls):
        '''The [network] section of config.ini (created when missing).'''
        config = cls._config().read_configuration(MeileGuiConfig.CONFFILE)
        if not config.has_section(PlanAPI.SECTION):
            config.add_section(PlanAPI.SECTION)
        return config[PlanAPI.SECTION]

    @classmethod
    def _stored_credentials(cls):
        section = cls._section()
        return (str(section.get(PlanAPI.USER, '') or '').strip(),
                str(section.get(PlanAPI.PASSWORD, '') or '').strip())

    @classmethod
    def _cached_token(cls):
        '''The token of config.ini while it is still valid, else ''.'''
        if cls._token and cls._expires > time() + PlanAPI.SKEW:
            return cls._token

        section = cls._section()
        token = str(section.get(PlanAPI.TOKEN, '') or '').strip()
        expires = cls._number(section.get(PlanAPI.EXPIRES, 0))
        if token and expires > time() + PlanAPI.SKEW:
            cls._token, cls._expires = token, expires
            return token
        return ''

    @staticmethod
    def _number(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def _register(cls):
        '''Register the account of this install and store it in config.ini.

        The shared secret is sent in the body.  The API accepts it as the
        X-Registration-Key header as well, and a live probe shows the header
        itself is fine - a GET of /register carrying it answers 405 (the normal
        answer to a GET) from both curl and Python.  The body is still the one
        used because it needs no header to survive a proxy: the API domain once
        answered with two A records and one of them dropped the connection, so
        a header-carrying request looked refused while the body got through.
        '''
        key = getattr(scrtsxx, 'REGISTRATION_KEY', None)
        body = {'key': str(key)} if key else {}

        request = HTTPRequests.MakeRequest(TIMEOUT=PlanAPI.TIMEOUT)
        http = request.hadapter()
        response = http.post(HTTParams.PLAN_API + HTTParams.API_REGISTER,
                             json=body)
        answer = cls._answer(response, 'Could not register with the Meile API')

        user = str(answer.get('username') or '').strip()
        password = str(answer.get('password') or '').strip()
        if not user or not password:
            raise RuntimeError('The Meile API did not return a username and a password')

        cls._store_account(user, password)
        print('Meile API account registered: %s' % user)
        return user, password

    @classmethod
    def _mint_token(cls):
        '''Ask /api/token for a token of the account of this install.'''
        user, password = cls.credentials()

        request = HTTPRequests.MakeRequest(TIMEOUT=PlanAPI.TIMEOUT)
        http = request.hadapter()
        response = http.get(HTTParams.PLAN_API + HTTParams.API_TOKEN,
                            auth=HTTPBasicAuth(user, password))
        answer = cls._answer(response, 'Could not authenticate with the Meile API')

        token = str(answer.get('token') or '').strip()
        if not token:
            raise RuntimeError('The Meile API did not return a token')

        duration = cls._number(answer.get('duration')) or PlanAPI.DURATION
        cls._token = token
        cls._expires = time() + duration
        cls._store_token(token, cls._expires)
        print('Meile API token renewed, valid for %d seconds' % int(duration))
        return token

    @staticmethod
    def _answer(response, message):
        '''Parsed body of a plan API answer, or an error carrying its text.'''
        try:
            answer = response.json()
        except Exception:
            answer = None

        if response.status_code in (200, 201) and isinstance(answer, dict):
            return answer

        detail = ''
        if isinstance(answer, dict):
            detail = str(answer.get('message') or '')
        elif isinstance(answer, str):
            detail = answer
        raise RuntimeError('%s: %s' % (message, detail or 'HTTP %s' % response.status_code))

    @classmethod
    def _store_account(cls, user, password):
        '''Persist the account and drop the token of the previous one.'''
        cls._token, cls._expires = None, 0.0
        cls._config().write_configuration(PlanAPI.SECTION, {
            PlanAPI.USER     : user,
            PlanAPI.PASSWORD : password,
            PlanAPI.TOKEN    : '',
            PlanAPI.EXPIRES  : 0,
        })

    @classmethod
    def _store_token(cls, token, expires):
        cls._config().write_configuration(PlanAPI.SECTION, {
            PlanAPI.TOKEN   : token,
            PlanAPI.EXPIRES : int(expires),
        })


