from django.dispatch import Signal

post_auth0_tokens = Signal(providing_args=["request", "token_info", "auth0_profile", "result"], use_caching=False)
post_auth0_callback = Signal(providing_args=["request", "user_info", "user"], use_caching=False)
