from fastapi import FastAPI
from app.api import users, clients, assets, allocations, movements
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Investmentpw API", version="1.0.0")

origins = [
    "http://localhost:3000",  
    "http://frontend:3000",   
    "http://localhost:8000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/auth", tags=["authentication"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])
app.include_router(allocations.router, prefix="/allocations", tags=["allocations"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])

@app.get("/")
def read_root():
    return {"message": "Investmentpw API"}