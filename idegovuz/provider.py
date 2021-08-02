from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class IdEgovUz(ProviderAccount):
    pass


class IdEgovUzProvider(OAuth2Provider):
    id = 'id.egov.uz'
    name = _("id.egov.uz")
    scope = [id]
    account_class = IdEgovUz

    def extract_uid(self, data):
        user_id = data.get('user_id')
        if not user_id:
            user_id = data.get('email')
        if not user_id:
            user_id = "{}-{}".format(data.get('first_name'), data.get('pport_no'))
        return user_id.lower()

    def extract_common_fields(self, data):
        return dict(first_name=data['first_name'],
                    last_name=data['sur_name'],
                    email=data.get('email'),
                    username=self.extract_uid(data))

    def get_auth_params(self, request, action):
        ret = super().get_auth_params(request, action)
        ret.update({'response_type': 'one_code', 'scope': self.scope})
        return ret

    def get_default_scope(self):
        return self.scope

    def sociallogin_from_response(self, request, response):
        sociallogin = super().sociallogin_from_response(request, response)
        return sociallogin


providers.registry.register(IdEgovUzProvider)
