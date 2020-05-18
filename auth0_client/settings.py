from django.conf import settings as django_settings

AUTH0_FORCE_HTTPS = getattr(django_settings, 'AUTH0_FORCE_HTTPS', True)
AUTH0_ERROR_TEMPLATE = getattr(django_settings, 'AUTH0_ERROR_TEMPLATE', 'auth0/error.html')
AUTH0_DOMAIN = django_settings.AUTH0_DOMAIN
AUTH0_CLIENT_ID = django_settings.AUTH0_CLIENT_ID
AUTH0_SECRET = django_settings.AUTH0_SECRET
AUTH0_AUDIENCE = getattr(django_settings, 'AUTH0_AUDIENCE', None)
AUTH0_AUTHENTICATION_BACKEND = getattr(django_settings, 'AUTH0_AUTHENTICATION_BACKEND', django_settings.AUTHENTICATION_BACKENDS[0])
AUTH0_DEFAULT_RETURN_TO = getattr(django_settings, 'AUTH0_DEFAULT_RETURN_TO', '/')
AUTH0_LOGOUT_RETURN_TO = getattr(django_settings, 'AUTH0_LOGOUT_RETURN_TO', '/')
AUTH0_MAP_INFO = getattr(django_settings, 'AUTH0_MAP_INFO', {
    'username': 'sub',
    'email': 'email',
    'user_metadata': '/claims/usermetadata',
})
REDIRECT_URL_SAME_ORIGIN = getattr(django_settings, 'REDIRECT_URL_SAME_ORIGIN', True)
