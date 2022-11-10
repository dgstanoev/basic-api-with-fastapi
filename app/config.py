from pydantic import BaseSettings


class Settings(BaseSettings):
    db_driver: str
    db_user: str
    db_password: str
    db_hostname: str
    db_port: str
    db_name: str
    algorithm: str
    secret: str
    access_token_expire_minutes: int
    sync_db: str

    class Config:
        env_file = '.env'


settings = Settings()
