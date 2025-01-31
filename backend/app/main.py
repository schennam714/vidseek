from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import upload
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    upload.router,
    prefix=settings.API_V1_STR + "/media",
    tags=["media"]
)

@app.get("/")
async def root():
    return {"message": "Multimedia Query Tool API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 