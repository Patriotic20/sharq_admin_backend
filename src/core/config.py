from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    access_token_expire_minutes: int = 30
    access_secret_key: str
    algorithm: str = "HS256"
    
    docs_username: str = "admin"
    docs_password: str = "admin123"
    
    amo_crm_base_url: str = "https://sharquniversity.amocrm.ru/api/v4"
    amo_crm_token: str
    
    base_url: str


    model_config = SettingsConfigDict(env_file=".env")

    @property
    def connection_string(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def amo_crm_config(self):
        return {
            "base_url": self.amo_crm_base_url,
            "token": self.amo_crm_token,
            "get_contract_pipline_id": 9646446,
            "get_contract_status_id": 78753886,
        }


settings = Settings()
