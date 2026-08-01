from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

# 1. Initialize the FastAPI application (like const app = express() in Node.js)
app = FastAPI(
    title="AI SQL Microservice",
    description="Generates read-only SQL queries from natural language and summarizes results.",
    version="1.0.0"
)

# 2. Add CORS Middleware (so Node.js or frontend can talk to it without browser blocking)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your Node.js backend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import router as utility_router
from app.api.auth_routes import router as auth_router
from app.api.connection_routes import router as connection_router
from app.api.query_routes import router as query_router

# 3. Mount our routers
# The utility router (health, etc)
app.include_router(utility_router, prefix="/api")

# The Auth router (signup, login, refresh)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# The Database Connections router
app.include_router(connection_router, prefix="/api/connections", tags=["Database Connections"])

# The Query Execution router
app.include_router(query_router, prefix="/api/query", tags=["Query Execution"])

# If you run this file directly, it will start the server
if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
