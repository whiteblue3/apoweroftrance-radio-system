from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    label = 'accounts'
    verbose_name = 'Accounts'

    def ready(self):
        import accounts.signals


# This is how we register our custom app config with Django. Django is smart
# enough to look for the `default_app_config` property of each registered app
# and use the correct app config based on that value.
default_app_config = 'accounts.AccountsConfig'
