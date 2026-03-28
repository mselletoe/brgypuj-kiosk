from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 12
    DEBUG: bool = True

    BACKUP_DIR: str = "./backups/barangay"

    # SMS Gateway (A7670E)
    SMS_PORT:        str   = "COM12"
    SMS_BAUD:        int   = 115200
    SMS_SMSC:        str   = "+639180000101"
    SMS_RETRIES:     int   = 3
    SMS_SEND_WAIT:   float = 15.0
    SMS_INTER_DELAY: float = 5.0

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()