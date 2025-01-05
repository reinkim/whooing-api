import functools

import requests

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

    # rule_file can be either a local file path or a URL.
    def read_all():
        if str(rule_file).startswith('http'):
            return _fetch_rules_from_url(rule_file)
        else:
            with open(rule_file, 'r') as fin:
                return fin.readlines()

    for l in read_all():
        l = l.strip()
        key, spend_type, display_name = l.split('\t', 2)
        rules.append(
            ItemMapping(name=key,
                        spend_type=spend_type,
                        display_name=display_name))

    return rules


def _fetch_rules_from_url(url):
    resp = requests.get(url, allow_redirects=True)
    resp.raise_for_status()
    lines = resp.content.decode().splitlines()
    # Let's assume the very first line is the header.
    if lines:
        return lines[1:]
    else:
        return []
