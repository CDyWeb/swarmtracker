""" Auth0 Views """
import json
import logging
import uuid
from urllib.parse import urlencode, urlunparse

import time
import jwt
import requests

from auth0.v3 import Auth0Error
from auth0.v3.authentication import GetToken
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language
from django.views import View
from django.urls import reverse
from jwt.algorithms import RSAAlgorithm
from swarm.models import SwarmUser as User

from . import post_auth0_callback, post_auth0_tokens, settings

logger = logging.getLogger(__name__)


def _auth_error(request, error='', template=None):
    """ Public: Generic error handler sends user to error page """
    if error:
        logger.error("Auth0 Error page: %s", error)

    template = template or settings.AUTH0_ERROR_TEMPLATE
    return render(request, template, {'error': error})


class Auth0View(View):
    session: dict = None
    callback_url: str = None
    _jwks: dict = None

    @property
    def jwks(self):
        if not self._jwks:
            self._jwks = requests.get(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json").json().get('keys')
        return self._jwks

    def get_jwk(self, kid):
        for jwk in self.jwks:
            if jwk['kid'] == kid:
                return jwk

    def get_auth_url(self, request: HttpRequest, prompt='none'):
        if not self.session:
            self._auth0_setup(request)

        # gets the requested url in next from django
        return_to = request.GET.get('next', self.session.get('auth0_return_to', settings.AUTH0_DEFAULT_RETURN_TO))
        if not return_to:
            return_to = reverse('home')

        # nonce
        self.session['auth0_nonce'] = uuid.uuid4().hex + uuid.uuid1().hex
        self.session['auth0_return_to'] = return_to

        auth0_domain = str(settings.AUTH0_DOMAIN)
        auth0_audience = settings.AUTH0_AUDIENCE or f"https://{auth0_domain}/userinfo"

        query = urlencode({
            'audience': auth0_audience,
            'client_id': settings.AUTH0_CLIENT_ID,
            'redirect_uri': self.callback_url,
            'state': self.session['auth0_nonce'],
            'prompt': prompt,
            'scope': 'openid profile email offline_access',
            'response_type': 'code',
            'language': get_language(),
        })
        return urlunparse(['https', auth0_domain, '/authorize', None, query, None])

    def _auth0_setup(self, request):
        self.session = getattr(request, 'session')
        scheme = 'https' if settings.AUTH0_FORCE_HTTPS else request.scheme
        self.callback_url = urlunparse([scheme, request.get_host(), reverse('auth0_callback'), None, None, None])
    
    def dispatch(self, request, *args, **kwargs):
        self._auth0_setup(request)
        return super().dispatch(request, *args, **kwargs)


class Auth0Login(Auth0View):

    def dispatch(self, request, *args, **kwargs):
        """ Public: Redirect user to Auth0 hosted login page """
        auth_url = self.get_auth_url(request)
        print(auth_url)
        return redirect(auth_url)


class Auth0Logout(View):

    def get(self, request):
        """ Public: Log user out of Django session """
        # Redirect to auth0 logout endpoint to get them out of /tenant/v2/logout
        # Important: This must be set in Auth0 account settings, Advanced.
        scheme = 'https' if settings.AUTH0_FORCE_HTTPS else request.scheme
        return_to = urlunparse([scheme, request.get_host(), settings.AUTH0_LOGOUT_RETURN_TO, None,
                                None, None]) if settings.REDIRECT_URL_SAME_ORIGIN else settings.AUTH0_LOGOUT_RETURN_TO

        query = urlencode({
            'client_id': settings.AUTH0_CLIENT_ID,
            'returnTo': return_to + request.GET.get('lang', '')
        })

        logout_url = urlunparse(['https', str(settings.AUTH0_DOMAIN), '/v2/logout', None, query, None])
        # then auth0 redirects back to where you want to go

        # Log user out of django session
        django_logout(request)

        return redirect(logout_url)


class Auth0Callback(Auth0View):

    def _process_tokens(self, request, token_info):
        """
        Process Auth0 Tokens and returns dict with username and email
        """
        try:
            """ Authorization Extension timeouts can prevent this. """
            assert 'expires_in' in token_info
            assert 'access_token' in token_info
            assert 'id_token' in token_info
        except AssertionError as e:
            logger.error(
                'Auth0 _token_property_check failed: %s', e)

            messages.add_message(request, messages.ERROR, mark_safe(_(
                'Login failed. Please contact our customer service team at <a href="tel:1-800-561-1268">1-800-561-1268</a>, or chat us using the chat window below.')))
            raise Auth0Error(400, 0, e)

        unverified_header = jwt.get_unverified_header(token_info['id_token'])
        jwk = self.get_jwk(unverified_header['kid'])
        if not jwk:
            raise ValueError('jwk not available')

        auth0_profile = jwt.decode(
            jwt=token_info['id_token'],
            key=RSAAlgorithm.from_jwk(json.dumps(jwk)),
            algorithms=["RS256"],
            audience=str(settings.AUTH0_CLIENT_ID),
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )
        auth0_profile['expires_at'] = token_info['expires_at']

        result = {
            'auth0_profile': auth0_profile,
            'username': auth0_profile['sub'],
            'expires_at': token_info['expires_at']
        }

        for result_key, profile_key in settings.AUTH0_MAP_INFO.items():
            result[result_key] = auth0_profile.get(profile_key)

        post_auth0_tokens.send(sender=self, request=request, token_info=token_info, auth0_profile=auth0_profile, result=result)

        return result

    def get(self, request):
        """
        Public: Handles callback for Auth0 uses GET and POST
        Initial login not refresh token
        """
        # verify state
        auth0_return_to = self.session.get('auth0_return_to', None)
        auth0_nonce = self.session.get('auth0_nonce', None)
        if not auth0_nonce or (auth0_nonce != request.GET.get('state')):
            logger.error('Auth0 nonce failed: %s')
            messages.add_message(request, messages.INFO, _('Login failed (wrong state). Please try again.'))
            return redirect(reverse('auth0_login'))

        # remove nonce
        self.session.pop('auth0_nonce')

        error = request.GET.get('error', None)
        if error:
            if error in ('login_required', 'consent_required', 'interaction_required'):
                return redirect(self.get_auth_url(request, 'login'))

            elif error == 'unauthorized':
                error_desc = request.GET.get('error_description')
                if error_desc == 'email_verification_required':
                    messages.add_message(request, messages.INFO, _('Please verify your email address.'))
            return _auth_error(request, error)

        # Generic error page, other than login required,
        # # present trouble logging you in with URL.

        # Call token endpoint
        domain = getattr(settings, 'AUTH0_DOMAIN')
        if domain is None or domain == '':
            domain = 'empirelife-dev.auth0.com'

        token_info = GetToken(domain).authorization_code(
            client_id=settings.AUTH0_CLIENT_ID,
            client_secret=settings.AUTH0_SECRET,
            code=request.GET.get('code'),
            redirect_uri=self.callback_url
        )

        try:
            if 'error' in token_info:
                return _auth_error(request, token_info.get('error_description'))

            token_info['expires_at'] = time.time() + float(token_info['expires_in'])
            user_info = self._process_tokens(request, token_info)

            if ('email_verified' in user_info) and (user_info['email_verified'] is False):
                return render(request, 'auth0/verify.html', {
                    'email': user_info.get('email')
                })

            # Login user to Django
            user = User.objects.filter(username=user_info['username']).first()
            if not user:
                user = User(username=user_info['username'])
                user.is_staff = False
                user.is_superuser = False
                user.auth0_profile = user_info.get('auth0_profile')
                user.save()

            user.email = user_info['email']
            user.backend = settings.AUTH0_AUTHENTICATION_BACKEND

            auth0_profile = user_info.get('auth0_profile')
            if auth0_profile.get('given_name', None):
                user.first_name = auth0_profile.get('given_name')
            if auth0_profile.get('family_name', None):
                user.last_name = auth0_profile.get('family_name')

            if user_info.get('user_metadata', None):
                if user_info.get('user_metadata').get('first_name', None):
                    user.first_name = user_info.get('user_metadata').get('first_name')
                if user_info.get('user_metadata').get('last_name', None):
                    user.last_name = user_info.get('user_metadata').get('last_name')

            user.save()

            django_login(request, user)

            # session mutation AFTER django_login, as this resets the session cookie
            request.session['profile'] = user_info['auth0_profile']
            request.session['refresh_token'] = token_info['refresh_token']
            request.session['auth0_token_info'] = token_info

            post_auth0_callback.send(sender=self, request=request, user_info=user_info, user=user)

        except Exception as e:
            # if e.redirect_to:
            #     return redirect(e.redirect_to)
            return _auth_error(request, str(e))
        return redirect(auth0_return_to)
