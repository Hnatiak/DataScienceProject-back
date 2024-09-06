import qrcode
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

env_file = Path(__file__).parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_from_name: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int
    cors_origins: str
    rate_limiter_times: int
    rate_limiter_seconds: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_app_prefix: str = "PhotoShare"
    # qr_error_correction: int = qrcode.constants.ERROR_CORRECT_M
    # qr_box_size: int = 7
    # qr_border: int = 4
    # qr_fill_color: str = "black"
    # qr_back_color: str = "white"

    model_config = ConfigDict(extra='ignore', env_file=env_file if env_file.exists() else None, env_file_encoding = "utf-8")

settings = Settings()
