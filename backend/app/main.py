from fastapi import FastAPI
import app.routers.test_router as test_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello SpotFinder!"}

app.include_router(test_router.router, prefix="/test", tags=["test"])