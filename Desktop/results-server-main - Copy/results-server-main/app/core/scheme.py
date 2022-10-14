# scheme.py
from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class DurinTokenScheme(OpenApiAuthenticationExtension):
    target_class = 'durin.auth.TokenAuthentication'
    name = 'DurinTokenAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': _(
                'Token-based authentication with required prefix "%s"'
            ) % "Token"
        }
