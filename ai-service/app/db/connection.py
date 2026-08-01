# SQLAlchemy is a Python ORM (Object-Relational Mapper). It lets us interact with
# a PostgreSQL database using Python classes and objects instead of raw SQL strings.
# It is similar to Prisma in Node.js.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Import our settings object to get the DATABASE_URL safely (no hardcoded passwords).
from app.core.config import settings


# create_engine() sets up the CONNECTION POOL.
# A connection pool is a set of database connections that are kept open and ready.
# When your code needs the DB, it grabs a connection from the pool (fast),
# uses it, and returns it back to the pool (instead of opening/closing a new one each time).
# Think of it like a restaurant with 5 tables already available.
# Every customer comes → the restaurant builds a new table, the customer eats, then the table is destroyed. This is slow.
#The restaurant already has 5 tables ready. A customer simply sits at an empty table, eats, leaves, and the table becomes available for the next customer.
engine = create_engine(
    settings.DATABASE_URL,  # The NeonDB URL from our .env file

    pool_size=5,            # Keep 5 connections permanently open and ready in the pool.

    max_overflow=10,        # If all 5 are busy at peak load, temporarily create up to 10 MORE.
                            # So the absolute maximum at any moment is 5 + 10 = 15 connections.
                            # These extra ones are closed automatically when traffic drops.

    pool_pre_ping=True,     # Before handing out a connection, send a tiny "ping" (SELECT 1)
                            # to verify the connection taken from pool is still alive. This is critical for
                            # NeonDB (serverless) because NeonDB aggressively closes idle connections
                            # after a few minutes. Without this, you'd get random "connection lost" errors.
                            # If NeonDB closed the idle connection,
                            # SQLAlchemy automatically creates a new one, preventing "connection lost" errors.
)


# sessionmaker creates a FACTORY for database sessions.
# A session is a single unit of work with the database (like a transaction).
# Every time you want to talk to the DB, you create a new session, do your work, and close it.
# autocommit=False: Changes are NOT saved automatically. You must call db.commit() explicitly.
# autoflush=False:  Changes are NOT sent to the DB until you explicitly commit or query.
# bind=engine:      All sessions created by this factory will use our connection pool above.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# declarative_base() creates a base class for all our SQLAlchemy database models (tables).
# Every class that inherits from Base (like SchemaEmbedding in vector_store.py)
# will be treated as a database table definition. SQLAlchemy reads these classes
# to know what columns and types to create in the database.
Base = declarative_base()


# get_db() is a DEPENDENCY GENERATOR — it will only be used in Phase B (FastAPI).
# FastAPI calls this function automatically for every incoming HTTP request.
# It creates a fresh session, hands it to the route handler, and guarantees
# the session is closed (returned to the pool) after the request finishes,
# even if an error occurs. The `yield` makes this a generator function.
# In Node.js terms, this is similar to a middleware that opens a DB connection
# per request and closes it in a finally block.
def get_db():
    db = SessionLocal()     # Open a session (grab a connection from the pool)
    try:
        yield db            # Hand the session to whoever called get_db() (FastAPI route)
    finally:
        db.close()          # ALWAYS close the session when done, whether success or error
