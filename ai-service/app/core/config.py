# pydantic-settings is a library that reads variables from a .env file and validates them.
# It is like Joi/Zod in Node.js. If a required variable is missing, the app crashes early
# with a clear error message instead of failing silently in production.
from pydantic_settings import BaseSettings, SettingsConfigDict


# BaseSettings is a special Pydantic class. Any variable you define inside it
# will be automatically read from your environment (i.e., from the .env file).
class Settings(BaseSettings):

    # --- Mistral AI ---
    # This is the API key to authenticate with Mistral's servers.
    # It has no default value, so if it's missing from .env, the app will refuse to start.
    MISTRAL_API_KEY: str

    # --- Database ---
    # The full NeonDB connection string. SQLAlchemy uses this to create the connection pool.
    # It has no default value — must exist in .env.
    DATABASE_URL: str

    # --- AI Model Names ---
    # The name of the Mistral model used for generating SQL from natural language.
    # "mistral-small-latest" is in Mistral's free tier.
    # These have defaults so the app works out of the box, but can be overridden in .env.
    MISTRAL_LLM_MODEL: str = "mistral-small-latest"

    # The name of the Mistral model used for converting text into vector embeddings.
    # "mistral-embed" is Mistral's dedicated embedding model (free tier).
    MISTRAL_EMBED_MODEL: str = "mistral-embed"

    # --- Security: JWT ---
    # Secret key used to sign and verify JWT tokens for React user sessions.
    # In production, generate a strong random value: python -c "import secrets; print(secrets.token_hex(32))"
    JWT_SECRET_KEY: str = "change_this_to_a_strong_random_secret_in_production"
    JWT_ALGORITHM: str = "HS256"          # The algorithm used to sign the token
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7 # Token expires after 7 days

    # --- Security: Encryption ---
    # Fernet symmetric key used to encrypt/decrypt user database URLs before storing in DB B.
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = "change_this_to_a_real_fernet_key_in_production"

    # --- App Settings ---
    # These three settings are NOT used in Phase 1. They are defined here now so that
    # when we add FastAPI in Phase B, we can simply call settings.APP_PORT without
    # hardcoding the number anywhere in the code. Think of it as future-proofing.
    APP_ENV: str = "development"    # "development" vs "production" — used to toggle debug mode
    APP_HOST: str = "0.0.0.0"      # "0.0.0.0" means listen on all network interfaces (not just localhost)
    APP_PORT: int = 8000            # The port the FastAPI server will run on (like :3000 in Node)

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # model_config tells pydantic-settings where to find the .env file.
    # env_file=".env" means look for a file named .env in the CURRENT WORKING DIRECTORY
    # (the folder you run the script from — which should always be ai-service/).
    # extra="ignore" means if there are extra variables in .env not listed above, ignore them silently.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# We create a single instance of Settings here at module level.
# This means the .env file is read exactly ONCE when this module is first imported.
# Any other file that does `from app.core.config import settings` will get
# this same pre-loaded object — no repeated disk reads, very efficient.
settings = Settings()
