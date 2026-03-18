from datetime import datetime, timedelta
import time

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker
import uvicorn

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    failed_attempts = Column(Integer, default=0, nullable=False)
    blocked_until = Column(DateTime, nullable=True)


def ensure_database_schema():
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns("users")}

    with engine.begin() as connection:
        if "failed_attempts" not in existing_columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")
            )
        if "blocked_until" not in existing_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN blocked_until DATETIME"))


ensure_database_schema()

app = FastAPI()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def senha_eh_fraca(password: str):
    if len(password) < 6 or len(password) > 15:
        return "A senha deve conter no minimo 6 caracteres e no maximo 15"
    if not any(c.isupper() for c in password):
        return "A senha deve conter pelo menos 1 caractere maiusculo"
    if not any(c.islower() for c in password):
        return "A senha deve conter pelo menos 1 caractere minusculo"
    if not any(c.isnumeric() for c in password):
        return "A senha deve conter pelo menos 1 caractere numerico"
    if not any(not c.isalnum() for c in password):
        return "A senha deve conter pelo menos 1 caractere especial"

    return None


@app.post("/register/")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ja existe",
        )

    result = senha_eh_fraca(request.password)
    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result,
        )

    user = User(
        username=request.username,
        email=request.email,
        password=request.password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Usuario registrado com sucesso!"}


@app.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
        )

    now = datetime.utcnow()
    if user.blocked_until and user.blocked_until > now:
        remaining_seconds = int((user.blocked_until - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Conta bloqueada temporariamente. Tente novamente em {remaining_seconds} segundos.",
        )

    if user.password != request.password:
        user.failed_attempts += 1
        delay_seconds = min(2 ** user.failed_attempts, 8)

        if user.failed_attempts >= 3:
            user.blocked_until = now + timedelta(minutes=5)

        db.commit()
        time.sleep(delay_seconds)

        detail = "Credenciais invalidas"
        if user.blocked_until and user.blocked_until > now:
            detail = "Credenciais invalidas. Conta bloqueada por 5 minutos apos 3 tentativas falhas."

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    user.failed_attempts = 0
    user.blocked_until = None
    db.commit()

    return {"message": "Login realizado com sucesso!"}


if __name__ == "__main__":
    uvicorn.run(
        "servico:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
