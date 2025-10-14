from fastapi import FastAPI
from app.routes import feature1, feature2, feature3

app = FastAPI(title="Resume Analysis Microservice")

# Register all features
app.include_router(feature1.router, prefix="/feature1", tags=["Feature 1"])
app.include_router(feature2.router, prefix="/feature2", tags=["Feature 2"])
app.include_router(feature3.router, prefix="/feature3", tags=["Feature 3"])

@app.get("/")
def root():
    return {"message": "Resume Analysis Microservice Running"}
