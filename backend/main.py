from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents_table

app = FastAPI(title="Kiosk Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(residents_table.router)

@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}