from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'radio'
    label = 'radio'
    verbose_name = 'Radio'

    def ready(self):
        import radio.signals


# This is how we register our custom app config with Django. Django is smart
# enough to look for the `default_app_config` property of each registered app
# and use the correct app config based on that value.
default_app_config = 'radio.AccountsConfig'
