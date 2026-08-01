from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

# Initialize the Fernet cipher suite using our secret encryption key
try:
    cipher_suite = Fernet(settings.ENCRYPTION_KEY)
except ValueError:
    # This happens if the key in .env is not a valid 32-byte base64-encoded string
    raise ValueError("Invalid ENCRYPTION_KEY in .env. Generate one using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")

def encrypt_db_url(db_url: str) -> str:
    """
    Encrypts the raw database connection string (which contains the user's password)
    so it can be safely stored in NeonDB.
    """
    # Fernet requires bytes, so we encode the string to bytes, encrypt it, 
    # and then decode the encrypted bytes back to a string for database storage.
    return cipher_suite.encrypt(db_url.encode("utf-8")).decode("utf-8")

def decrypt_db_url(encrypted_url: str) -> str:
    """
    Decrypts the stored connection string back into a usable URL.
    Only the Python backend has the ENCRYPTION_KEY, so only Python can do this.
    """
    try:
        return cipher_suite.decrypt(encrypted_url.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise ValueError("Failed to decrypt the database URL. The encryption key may have changed.")
