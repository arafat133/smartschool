import os

class Settings:
    PROJECT_NAME: str = "Secure Cloud School System"
    # Using Render.com external URL with asyncpg
    DATABASE_URL: str = "postgresql+asyncpg://secure_school_user:1Of5TMWyOnwaaQwqM9if4D4BEvaoYLRb@dpg-d98ktj67r5hc73d9ulug-a.oregon-postgres.render.com/secure_school"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_for_jwt_tokens_generation")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

settings = Settings()
