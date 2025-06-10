from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.victim_routes import router as victim_router
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from app.auth.auth_utils import create_access_token, fake_users_db
from app.auth.auth_models import Token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(victim_router, prefix="/victims", tags=["Victims"])

@app.get("/")
def root():
    return {"message": "Human Rights Monitor API is running!"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = fake_users_db.get(form_data.username)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid username")
    access_token = create_access_token(
        data={"sub": user_data["username"], "role": user_data["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
