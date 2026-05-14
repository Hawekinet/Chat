from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Field, Session, SQLModel, create_engine, select

SECRET_KEY = "local-chat-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 24

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "chat.db"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI(title="Local LAN Chat API")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="user")
    is_active: bool = Field(default=True)


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(index=True)
    sender_username: str
    content: str = ""
    media_type: str = "text"
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


@app.on_event("startup")
def startup() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            session.add(
                User(
                    username="admin",
                    password_hash=pwd_context.hash("admin123"),
                    role="admin",
                )
            )
            session.commit()


def create_token(user: User) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.post("/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == form_data.username)).first()
        if not user or not pwd_context.verify(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(user), "token_type": "bearer", "role": user.role}


@app.post("/admin/users")
def create_local_user(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    _: User = Depends(require_admin),
):
    if role not in {"admin", "user"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    with Session(engine) as session:
        exists = session.exec(select(User).where(User.username == username)).first()
        if exists:
            raise HTTPException(status_code=409, detail="Username already exists")
        user = User(username=username, password_hash=pwd_context.hash(password), role=role)
        session.add(user)
        session.commit()
    return {"message": "User created"}


@app.get("/messages")
def get_messages(user: User = Depends(get_current_user)):
    with Session(engine) as session:
        messages = session.exec(select(ChatMessage).order_by(ChatMessage.created_at)).all()
    return {"items": messages, "viewer": user.username, "role": user.role}


@app.post("/messages")
async def post_message(
    content: str = Form(""),
    media_type: str = Form("text"),
    file: Optional[UploadFile] = File(default=None),
    user: User = Depends(get_current_user),
):
    file_name = None
    file_path = None
    if file:
        safe_name = f"{datetime.utcnow().timestamp()}_{file.filename}"
        target = UPLOADS_DIR / safe_name
        data = await file.read()
        target.write_bytes(data)
        file_name = file.filename
        file_path = str(target)

    message = ChatMessage(
        sender_id=user.id,
        sender_username=user.username,
        content=content,
        media_type=media_type,
        file_name=file_name,
        file_path=file_path,
    )
    with Session(engine) as session:
        session.add(message)
        session.commit()
        session.refresh(message)
    return message


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
