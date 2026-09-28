from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    catalog_service_url: str = "http://127.0.0.1:8001"
    payment_service_url: str = "http://127.0.0.1:8003"
    rabbitmq_url: str
    payment_succeeded_routing_key: str = "payment.succeeded"
    payment_queue_name: str = "payment.results"
    payment_exchange_name: str = "payment.events"


settings = Settings()


class NotFoundError(Exception):
    pass
