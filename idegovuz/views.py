import time
import requests
from allauth.socialaccount.helpers import render_authentication_error, complete_social_login

from allauth.socialaccount.models import SocialToken, SocialLogin
from allauth.socialaccount.providers.base import AuthError, ProviderException
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter, OAuth2LoginView, OAuth2View)
from allauth.utils import get_request_param
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from requests import RequestException

from .constants import *
from .provider import IdEgovUzProvider


class IdEgovUzAdapter(OAuth2Adapter):
    provider_id = IdEgovUzProvider.id
    base_url = BASE_URL
    authorize_url = AUTHORIZE_URL
    access_token_url = ACCESS_TOKEN_URL
    profile_url = PROFILE_URL

    def get_callback_url(self, request, app):
        if not settings.DEBUG:
            return '{}/accounts/id.gov.uz/login/callback'.format(settings.SITE_DOMAIN_NAME)
        return super().get_callback_url(request, app)

    def complete_login(self, request, app, access_token, **kwargs):
        secrets = {
            'client_id': app.client_id,
            'client_secret': app.secret,
            'grant_type': 'one_access_token_identify',
            'access_token': access_token.token,
            'scope': app.client_id
        }
        resp = requests.post(self.profile_url, data=secrets)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def parse_token(self, data):
        token = SocialToken(token=data['access_token'])
        token.token_secret = data.get('refresh_token', '')
        expires_in = data.get(self.expires_in_key, None)
        if expires_in:
            # in response id.egov.uz returns date in long timestamp format instead of expire time in seconds
            expires_date = timezone.datetime.strptime(
                time.ctime(expires_in / 1000), "%a %b %d %H:%M:%S %Y")
            token.expires_at = timezone.make_aware(expires_date)
        return token


class OAuth2CallbackView(OAuth2View):
    def dispatch(self, request, *args, **kwargs):
        if "error" in request.GET or "code" not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get("error", None)
            if auth_error == self.adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request, self.adapter.provider_id, error=error
            )
        app = self.adapter.get_provider().get_app(self.request)
        client = self.get_client(self.request, app)

        try:
            print("APP", app)
            print("CLIENT", client)
            access_token = self.adapter.get_access_token_data(
                request, app, client)
            token = self.adapter.parse_token(access_token)
            token.app = app
            login = self.adapter.complete_login(
                request, app, token, response=access_token
            )
            login.token = token
            if self.adapter.supports_state:
                login.state = SocialLogin.verify_and_unstash_state(
                    request, get_request_param(request, "state")
                )
            else:
                login.state = SocialLogin.unstash_state(request)

            return complete_social_login(request, login)
        except (
                PermissionDenied,
                OAuth2Error,
                RequestException,
                ProviderException,
        ) as e:
            print("ERROR")
            print(e)
            return render_authentication_error(
                request, self.adapter.provider_id, exception=e
            )


oauth2_login = OAuth2LoginView.adapter_view(IdEgovUzAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(IdEgovUzAdapter)
