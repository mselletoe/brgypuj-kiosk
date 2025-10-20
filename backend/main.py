from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents_table, auth

app = FastAPI(title="Kiosk Backend API")

# CORS setup
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(residents_table.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}