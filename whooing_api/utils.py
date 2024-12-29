import functools

import sentry_sdk

from .settings import Settings
from .category_table import ItemMapping


@functools.lru_cache
def get_settings():
    return Settings()


def init_sentry():
    settings = get_settings()
    if settings.sentry_dsn != None and settings.sentry_dsn.get_secret_value():
        sentry_sdk.init(
            dsn=settings.sentry_dsn.get_secret_value(),
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for tracing.
            traces_sample_rate=0.0,
            _experiments={
                # Set continuous_profiling_auto_start to True
                # to automatically start the profiler on when
                # possible.
                #"continuous_profiling_auto_start": False,
            },
        )


def get_rules(rule_file):
    if not rule_file:
        return []

    rules = []
    with open(rule_file, 'r') as fin:
        for l in fin.readlines():
            l = l.strip()
            key, spend_type, display_name = l.split('\t', 2)
            rules.append(
                ItemMapping(name=key,
                            spend_type=spend_type,
                            display_name=display_name))

    return rules


def get_webhook_url():
    token = get_settings().whooing_token
    if not token or not token.get_secret_value():
        raise RuntimeError('invalid webhook URL for whooing')

    return f'https://whooing.com/webhook/s/{token.get_secret_value()}/'
