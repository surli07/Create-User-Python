from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# FastAPI app instance
app = FastAPI()

# Middleware untuk CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua origin 
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua metode HTTP
    allow_headers=["*"],  # Mengizinkan semua header
)

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    identity_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model for request data
class UserCreate(BaseModel):
    name: str
    identity_number: str
    email: str
    date_of_birth: date  # Pastikan format ini sesuai dengan input JSON

class UserResponse(BaseModel):
    id: int
    name: str
    identity_number: str
    email: str
    date_of_birth: date

    class Config:
        orm_mode = True


# API endpoint to create an user
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user




if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)