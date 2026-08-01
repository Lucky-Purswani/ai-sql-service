import asyncio
from app.db.connection import engine, Base
from app.db.models import User, EmailVerification, RefreshToken, DatabaseConnection, AuditLog, LoginAudit
from app.db.vector_store import SchemaEmbedding

def init_db():
    print("Creating database tables in NeonDB...")
    # This will create all tables defined in models that inherit from Base
    # It will NOT drop existing tables or overwrite data.
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    init_db()
