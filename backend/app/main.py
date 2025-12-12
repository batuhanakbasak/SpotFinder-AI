from fastapi import FastAPI

# Routers
from app.routers import test_router

app = FastAPI(
    title="SpotFinder AI Backend",
    version="1.0.0",
)

@app.get("/")
def home():
    return {"message": "SpotFinder Backend is running"}

# Register routers
app.include_router(test_router.router, prefix="/test", tags=["test"])