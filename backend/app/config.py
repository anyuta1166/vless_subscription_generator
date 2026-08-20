from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "db"
    db_port: int = 3306
    db_name: str = "vless_subscriptions"
    db_user: str = "vless"
    db_password: str

    public_base_url: str

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )


settings = Settings()
