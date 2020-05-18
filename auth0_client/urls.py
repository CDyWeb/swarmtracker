from django.conf.urls import url

from .views import Auth0Login, Auth0Callback, Auth0Logout, _auth_error

urlpatterns = [
    url(r'^login$', Auth0Login.as_view(), name='auth0_login'),
    url(r'^callback$', Auth0Callback.as_view(), name='auth0_callback'),
    url(r'^logout$', Auth0Logout.as_view(), name='auth0_logout'),
    url(r'^auth/error$', _auth_error, name='auth0_error'),
]
