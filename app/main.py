from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.clusters import router as cluster_router
from app.api.search import router as search_router

app = FastAPI(title="AI Document Organizer")

app.include_router(upload_router)
app.include_router(cluster_router)
app.include_router(search_router)

# register routes
app.include_router(upload_router)

@app.get("/")
def root():
    return {
        "message": "AI Document Organizer backend is running"
    }
