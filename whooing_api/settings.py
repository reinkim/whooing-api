from typing import Optional, Set

from pydantic import Field, FilePath, HttpUrl, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    # Whooing
    ## 미리 지정한 규칙이 들어있는 tsv 파일 경로
    rules: Optional[FilePath] = Field(default=None)

    ## Whooing webhook token. For example, '1234-1234-1234-1234-1234'
    ## https://whooing.com/#main/setting 하단에서 확인 가능
    whooing_token: Secret[str]

    # Sentry DSN (optional)
    ## For example, https://abcdef123456.ingest.us.sentry.io/1234567890
    sentry_dsn: Optional[Secret[HttpUrl]] = Field(default=None)
