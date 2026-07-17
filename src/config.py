from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/casa_monarca"
    SUPABASE_JWT_SECRET: str = "default_secret_change_me_in_production"
    RESEND_API_KEY: str = "default_key"
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "default_user@gmail.com"
    SMTP_PASSWORD: str = "default_password"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
