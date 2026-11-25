#!/usr/bin/env python3
'''
Standalone test for the plan API account/token client of the app
(cli/plan_api.py).

`requests` is not needed: the auth classes, the HTTP session and the pyarmor
scrtsxx module are replaced with small stand-ins, while the real
conf/meile_config.py and typedef/konstants.py are loaded, so the config file
handling and the constants under test are the ones the app ships.  Run with:

    python3 tests/plan_api_test.py
'''

import configparser
import importlib.util
import os
import sys
import tempfile
import threading
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'src')
CLIENT = os.path.join(SRC, 'cli', 'plan_api.py')

REGISTRATION_KEY = 'reg-key-123'
USER = 'meile_abc123'
PASSWORD = 's3cret-token-urlsafe'
TOKEN = 'header.payload.signature'


# --------------------------------------------------------------- stand-ins
class FakeAuthBase():
    '''Stand-in for requests.auth.AuthBase.'''

    def __call__(self, request):
        return request


class FakeHTTPBasicAuth(FakeAuthBase):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class FakeResponse():
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession():
    '''Records the calls and answers them from a scripted queue.'''

    def __init__(self):
        self.calls = []
        self.answers = []

    def _call(self, method, url, **kwargs):
        self.calls.append({'method': method, 'url': url,
                           'json': kwargs.get('json'),
                           'headers': kwargs.get('headers'),
                           'auth': kwargs.get('auth')})
        if not self.answers:
            raise AssertionError('unexpected %s %s' % (method, url))
        return self.answers.pop(0)

    def get(self, url, **kwargs):
        return self._call('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._call('POST', url, **kwargs)


class FakeHTTPRequests():
    '''Stand-in for adapters.HTTPRequests (one shared session).'''

    def __init__(self, session):
        self.session = session

    def MakeRequest(self, TIMEOUT=None, headers=None):
        return self

    def hadapter(self):
        return self.session


class FakeRequest():
    '''Stand-in for a requests PreparedRequest (headers + response hooks).'''

    def __init__(self, headers=None, hooks=None):
        self.headers = dict(headers or {})
        self.hooks = {'response': list(hooks or [])}

    def copy(self):
        return FakeRequest(self.headers, self.hooks.get('response'))

    def register_hook(self, name, hook):
        self.hooks.setdefault(name, []).append(hook)


class FakeRetryResponse():
    '''Stand-in for a requests Response of the token replay path.'''

    def __init__(self, status_code, request=None, connection=None):
        self.status_code = status_code
        self.request = request
        self.connection = connection
        self.history = []
        self.drained = False
        self.closed = False

    @property
    def content(self):
        self.drained = True
        return b''

    def close(self):
        self.closed = True


class FakeConnection():
    '''Stand-in for the urllib3 connection of a response.'''

    def __init__(self, answer):
        self.answer = answer
        self.sent = []

    def send(self, request, **kwargs):
        self.sent.append({'request': request, 'kwargs': kwargs})
        self.answer.request = request
        return self.answer


# ------------------------------------------------------------------ loading
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_real = {}


def real_modules():
    '''The real typedef/konstants.py and conf/meile_config.py (stdlib only).

    They are loaded once and their paths are pointed at a temporary directory
    right away, so no test - and no mistake in one - can touch the
    configuration file of the machine the test runs on.
    '''
    if not _real:
        typedef = types.ModuleType('typedef')
        sys.modules['typedef'] = typedef
        konstants = load('typedef.konstants',
                         os.path.join(SRC, 'typedef', 'konstants.py'))
        typedef.konstants = konstants

        conf = types.ModuleType('conf')
        sys.modules['conf'] = conf
        config = load('conf.meile_config',
                      os.path.join(SRC, 'conf', 'meile_config.py'))
        conf.meile_config = config

        _real['konstants'] = konstants
        _real['config'] = config
        fresh_config(config)

    return _real['konstants'], _real['config']


def load_client(session, registration_key=REGISTRATION_KEY):
    '''Load cli/plan_api.py against stand-ins for its non-stdlib imports.

    The real typedef/konstants.py and conf/meile_config.py are loaded (both are
    stdlib only), so the constants and the config file handling are the ones
    the app ships.  Returns (client module, konstants, meile_config).
    '''
    konstants, config = real_modules()

    # requests is not installed in the test environment.
    requests = types.ModuleType('requests')
    auth = types.ModuleType('requests.auth')
    auth.AuthBase = FakeAuthBase
    auth.HTTPBasicAuth = FakeHTTPBasicAuth
    requests.auth = auth

    scrtsxx = types.ModuleType('scrtsxx')
    if registration_key:
        scrtsxx.REGISTRATION_KEY = registration_key

    dist = types.ModuleType('fiat.stripe_pay.dist')
    dist.scrtsxx = scrtsxx
    stripe_pay = types.ModuleType('fiat.stripe_pay')
    stripe_pay.dist = dist
    fiat = types.ModuleType('fiat')
    fiat.stripe_pay = stripe_pay

    adapters = types.ModuleType('adapters')
    adapters.HTTPRequests = FakeHTTPRequests(session)

    modules = {
        'requests'            : requests,
        'requests.auth'       : auth,
        'fiat'                : fiat,
        'fiat.stripe_pay'     : stripe_pay,
        'fiat.stripe_pay.dist': dist,
        'adapters'            : adapters,
    }
    saved = {name: sys.modules.get(name) for name in modules}
    sys.modules.update(modules)

    try:
        client = load('plan_api_client', CLIENT)
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value

    return client, konstants, config


# ------------------------------------------------------------------ helpers
def fresh_config(config):
    '''Point the config of the app at a private file for one scenario.

    MeileGuiConfig keeps the paths as class attributes (the app uses
    ~/.meile-gui), so the whole class is redirected here - a test must never
    read or write the configuration of the machine it runs on.
    '''
    meile = config.MeileGuiConfig
    basedir = tempfile.mkdtemp(prefix='meile-gui-plan-api-')
    meile.BASEDIR = basedir
    meile.BASEBINDIR = os.path.join(basedir, 'bin')
    meile.CONFFILE = os.path.join(basedir, 'config.ini')
    meile.IMGDIR = os.path.join(basedir, 'img')
    meile.LAUNCHD_PATH = os.path.join(basedir, 'launchd')
    # The app shares one parser for the life of the process; a test needs a
    # clean one for every config file it writes.
    meile.CONFIG = configparser.ConfigParser()
    return meile.CONFFILE


def read_config(confpath):
    parser = configparser.ConfigParser()
    parser.read(confpath)
    return parser


def write_config(config, section, values):
    '''Write into the config file through the real MeileGuiConfig helper.'''
    return config.MeileGuiConfig().write_configuration(section, values)


def scenario(session, config, client):
    '''A fresh config file, a fresh token cache and an empty call log.'''
    confpath = fresh_config(config)
    client.MeilePlanAPI._token = None
    client.MeilePlanAPI._expires = 0.0
    session.calls = []
    session.answers = []
    return confpath


def main():
    failures = []

    def check(name, condition):
        print(('PASS' if condition else 'FAIL') + ': ' + name)
        if not condition:
            failures.append(name)

    session = FakeSession()
    client, konstants, config = load_client(session)

    api = client.MeilePlanAPI
    plan = konstants.PlanAPI
    htt = konstants.HTTParams
    base = htt.PLAN_API

    # ---------------------------------------------------------- registration
    confpath = scenario(session, config, client)
    write_config(config, 'wallet', {'uuid': 'test-uuid'})
    session.answers = [FakeResponse({'status': True, 'username': USER,
                                     'password': PASSWORD}, 201)]
    check('a fresh install registers its own account',
          api.credentials() == (USER, PASSWORD))
    check('... against /register',
          session.calls[-1]['url'] == base + htt.API_REGISTER)
    check('... with the registration key in the body',
          session.calls[-1]['json'].get('key') == REGISTRATION_KEY)
    check('... and no secret in a header',
          not session.calls[-1]['headers']
          or 'X-Registration-Key' not in session.calls[-1]['headers'])

    stored = read_config(confpath)[plan.SECTION]
    check('the account is stored in the [network] section of config.ini',
          stored.get(plan.USER) == USER and stored.get(plan.PASSWORD) == PASSWORD)
    check('... under the documented keys',
          (plan.USER, plan.PASSWORD) == ('muser', 'mpassword'))
    check('... without a token', stored.get(plan.TOKEN, '') == '')
    check('... keeping the rest of the config file',
          read_config(confpath)['wallet'].get('uuid') == 'test-uuid')

    calls = len(session.calls)
    check('a stored account is reused', api.credentials() == (USER, PASSWORD))
    check('... without asking the API again', len(session.calls) == calls)

    # ---------------------------------------------------------------- token
    session.answers = [FakeResponse({'token': TOKEN, 'duration': 600})]
    check('the token is minted', api.token() == TOKEN)
    check('... against /api/token', session.calls[-1]['url'] == base + htt.API_TOKEN)
    check('... with the basic auth of the account',
          isinstance(session.calls[-1]['auth'], FakeHTTPBasicAuth)
          and session.calls[-1]['auth'].username == USER
          and session.calls[-1]['auth'].password == PASSWORD)

    stored = read_config(confpath)[plan.SECTION]
    check('the token is stored in config.ini', stored.get(plan.TOKEN) == TOKEN)
    check('... with its expiry',
          float(stored.get(plan.EXPIRES)) > time.time() + plan.SKEW)

    calls = len(session.calls)
    check('the cached token is reused', api.token() == TOKEN)
    check('... without asking the API again', len(session.calls) == calls)

    # A restart starts with an empty cache: the token of the file is used.
    api._token, api._expires = None, 0.0
    check('the token of config.ini survives a restart', api.token() == TOKEN)
    check('... without asking the API again', len(session.calls) == calls)

    # An expired token, or one inside the skew, is renewed.
    api._token, api._expires = None, 0.0
    write_config(config, plan.SECTION, {plan.EXPIRES: int(time.time()) - 10})
    session.answers = [FakeResponse({'token': 'new-token', 'duration': 600})]
    check('an expired token is renewed', api.token() == 'new-token')
    check('... with one call to /api/token', len(session.calls) == calls + 1)

    api._token, api._expires = None, 0.0
    write_config(config, plan.SECTION,
                               {plan.EXPIRES: int(time.time()) + plan.SKEW - 1})
    session.answers = [FakeResponse({'token': 'newer-token', 'duration': 600})]
    check('a token inside the skew is renewed', api.token() == 'newer-token')

    # ----------------------------------------------------------- call shape
    api._token, api._expires = None, 0.0
    write_config(config, plan.SECTION, {plan.TOKEN: TOKEN,
                                              plan.EXPIRES: int(time.time()) + 600})
    calls = len(session.calls)
    check('the headers of a call carry the bearer token',
          api.headers() == {'Authorization': 'Bearer ' + TOKEN})

    request = FakeRequest()
    api.auth()(request)
    check('the auth object sets the same header',
          request.headers['Authorization'] == 'Bearer ' + TOKEN)
    check('... and registers one response hook',
          len(request.hooks['response']) == 1)
    check('... without asking the API', len(session.calls) == calls)

    # ------------------------------------------------- a refused token (401)
    api._token, api._expires = None, 0.0
    write_config(config, plan.SECTION, {plan.TOKEN: 'stale',
                                              plan.EXPIRES: int(time.time()) + 600})
    session.calls = []
    session.answers = [FakeResponse({'token': 'fresh', 'duration': 600})]

    request = FakeRequest()
    api.auth()(request)
    check('a call carries the cached token',
          request.headers['Authorization'] == 'Bearer stale')

    connection = FakeConnection(FakeRetryResponse(200))
    refused = FakeRetryResponse(401, request=request, connection=connection)
    replayed = request.hooks['response'][0](refused)

    check('a 401 mints a new token', session.calls[-1]['url'] == base + htt.API_TOKEN)
    check('... and replays the request with it',
          connection.sent[0]['request'].headers['Authorization'] == 'Bearer fresh')
    check('... only once',
          connection.sent[0]['request'].headers.get(client.RETRY_HEADER) == '1')
    check('... returning the replayed answer', replayed is connection.answer)
    check('... with the refused one in its history', replayed.history == [refused])
    check('... after draining and closing it', refused.drained and refused.closed)

    again = FakeRetryResponse(401, request=connection.sent[0]['request'],
                              connection=connection)
    calls = len(session.calls)
    check('a replayed request is not replayed again',
          request.hooks['response'][0](again) is again)
    check('... without asking for another token', len(session.calls) == calls)

    # A banned account (403) must not be retried: the credentials are refused
    # on purpose and re-registering would be ban evasion.
    session.calls = []
    session.answers = []
    request = FakeRequest()
    api.auth()(request)
    banned = FakeRetryResponse(403, request=request)
    check('a 403 is not retried', request.hooks['response'][0](banned) is banned)
    check('... without asking the API', session.calls == [])

    # ------------------------------------------------------- API failures
    confpath = scenario(session, config, client)
    session.answers = [FakeResponse({'status': False,
                                     'message': 'Invalid registration key'}, 403)]
    try:
        api.credentials()
        check('a refused registration raises', False)
    except Exception as e:
        check('a refused registration raises', 'Invalid registration key' in str(e))
    check('... and stores nothing',
          read_config(confpath)[plan.SECTION].get(plan.USER, '') == '')

    confpath = scenario(session, config, client)
    write_config(config, plan.SECTION, {plan.USER: USER,
                                              plan.PASSWORD: PASSWORD})
    session.answers = [FakeResponse({'status': False,
                                     'message': 'Authentication required'}, 401)]
    try:
        api.token()
        check('a refused token raises', False)
    except Exception as e:
        check('a refused token raises', 'Authentication required' in str(e))

    confpath = scenario(session, config, client)
    write_config(config, plan.SECTION, {plan.USER: USER,
                                              plan.PASSWORD: PASSWORD})
    session.answers = [FakeResponse({'status': True, 'username': USER,
                                     'password': PASSWORD}, 201)]
    try:
        api.token()
        check('an answer without a token raises', False)
    except Exception:
        check('an answer without a token raises', True)

    # ------------------------------------------------------ concurrency
    confpath = scenario(session, config, client)
    session.answers = [FakeResponse({'status': True, 'username': USER,
                                     'password': PASSWORD}, 201)]
    results = []
    threads = [threading.Thread(target=lambda: results.append(api.credentials()))
               for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    check('concurrent first calls register one account',
          results == [(USER, PASSWORD)] * 5 and len(session.calls) == 1)

    confpath = scenario(session, config, client)
    write_config(config, plan.SECTION, {plan.USER: USER,
                                              plan.PASSWORD: PASSWORD})
    session.answers = [FakeResponse({'token': TOKEN, 'duration': 600})]
    results = []
    threads = [threading.Thread(target=lambda: results.append(api.token()))
               for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    check('concurrent calls mint one token',
          results == [TOKEN] * 5 and len(session.calls) == 1)

    # ------------------------------------------------- the registration key
    other_session = FakeSession()
    other, _, _ = load_client(other_session, registration_key=None)
    fresh_config(config)
    other_session.answers = [FakeResponse({'status': True, 'username': 'u',
                                           'password': 'p'}, 201)]
    other.MeilePlanAPI.credentials()
    check('the registration key is optional',
          not other_session.calls[-1]['headers']
          and other_session.calls[-1]['json'] == {})

    print()
    if failures:
        print('%s checks FAILED' % len(failures))
        return 1
    print('All plan API account/token tests passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())


