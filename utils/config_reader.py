from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr
    highest_admin_username: str
    password: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    def get_highest_admin_usernames(self):
        return self.highest_admin_username.split(',')

config = Settings()
