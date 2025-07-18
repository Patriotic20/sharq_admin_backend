from fastapi import FastAPI
from src.api import api_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from src.core.docs_auth import DocsAuthMiddleware

app = FastAPI(title="Sharq Admissions API", description="API for the Admissions system")

# Mount the uploads directory to serve static files
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



app.include_router(api_router)
app.add_middleware(DocsAuthMiddleware)

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://qabul2.sharqedu.uz",
        "https://qabul.sharqedu.uz",
        "https://admin.sharqedu.uz",
        "https://qabul.nsumt.uz",
        "https://marketing.nsumt.uz",
        "http://dashboard.sharqedu.uz",
        "https://dashboard.sharqedu.uz",
        "https://www.dashboard.sharqedu.uz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
