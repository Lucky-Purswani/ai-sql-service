from app.core.config import settings

print("SUCCESS: Config loaded successfully!")
print(f"Environment: {settings.APP_ENV}")
print(f"LLM Model: {settings.MISTRAL_LLM_MODEL}")
print(f"Embed Model: {settings.MISTRAL_EMBED_MODEL}")
print(f"Database URL length: {len(settings.DATABASE_URL)} chars (loaded safely)")
print(f"Mistral API Key loaded: {'Yes' if settings.MISTRAL_API_KEY else 'No'}")
