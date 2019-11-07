"""Only to getting configuration set in project's settings.py"""
from django.conf import settings as django_settings

from paytm.exceptions import IncorrectConfiguration


class Configuration(object):
    """Class to get configuration and then testing its format correctness"""

    MID = ''
    KEY = ''
    INDUSTRY = 'Retail'
    WEBSITE = 'WEBSTAGING'
    DEBUG = True

    CHANNEL_WEBSITE = 'WEB'
    CHANNEL_MOBILE_APP = 'WAP'
    STAGING_DOMAIN = 'securegw-stage.paytm.in'
    PRODUCTION_DOMAIN = 'securegw.paytm.in'

    settings_mapping = {
        # Key: (attr, type, required, defaults)
        'PAYTM_MERCHANT_ID': ('MID', str, True, MID),
        'PAYTM_MERCHANT_KEY': ('KEY', str, True, KEY),
        'PAYTM_INDUSTRY': ('INDUSTRY', str, True, INDUSTRY),
        'PAYTM_WEBSITE': ('WEBSITE', str, True, WEBSITE),

        'PAYTM_DEBUG': ('DEBUG', bool, False, DEBUG),

        'PAYTM_CHANNEL_WEBSITE': ('CHANNEL_WEBSITE', str, False, CHANNEL_WEBSITE),
        'PAYTM_CHANNEL_MOBILE_APP': ('CHANNEL_MOBILE_APP', str, False, CHANNEL_MOBILE_APP),

        'PAYTM_STAGING_DOMAIN': ('STAGING_DOMAIN', str, False, STAGING_DOMAIN),
        'PAYTM_PRODUCTION_DOMAIN': ('PRODUCTION_DOMAIN', str, False, PRODUCTION_DOMAIN)
    }

    def __init__(self):
        # Get the values from settings and then set attribute
        for key in self.settings_mapping:
            setattr(
                self,
                self.settings_mapping[key][0],
                self._get(key)
            )

        if self.DEBUG:
            self.DOMAIN = self.STAGING_DOMAIN
        else:
            self.DOMAIN = self.PRODUCTION_DOMAIN

        # deleting for safety
        delattr(self, 'STAGING_DOMAIN')
        delattr(self, 'PRODUCTION_DOMAIN')

        self.merchant_credentials = {
            "MID": self.MID,
            "WEBSITE": self.WEBSITE,
            "INDUSTRY_TYPE_ID": self.INDUSTRY,
        }

    def _get(self, name):
        """Gets a particular settings from django_settings and checks its correctness"""

        attr_name, attr_type, required, default = self.settings_mapping[name]

        if required:
            try:
                value = getattr(django_settings, name)
            except AttributeError:
                # Raise
                raise IncorrectConfiguration('Please, add {} in your settings.py'.format(name))
        else:
            value = getattr(django_settings, name, default)

        if type(value) != attr_type:
            raise IncorrectConfiguration(
                '{} has incorrect type, required {} got {}'.format(name, attr_type, type(value))
            )

        return value
